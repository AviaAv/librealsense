/**
 * Real Device E2E Tests
 * 
 * These tests run against actual RealSense hardware.
 * They are tagged with @real-device and only run when REAL_DEVICE=true.
 * 
 * Prerequisites:
 * - RealSense camera connected via USB
 * - Backend API server running (python -m uvicorn main:combined_app --port 8000)
 * - Frontend dev server running (npm run dev)
 * 
 * Usage:
 *   REAL_DEVICE=true npx playwright test --project=real-device
 */

import { test, expect, getApiUrl, suppressWelcomeModal, dismissToasts, clickAll } from './fixtures'
import type { Locator, Page } from '@playwright/test'
import type { SensorInfo } from '../../src/api/types'

// Per-stream toggles only render inside an expanded sensor module
async function expandSensorModules(deviceCard: Locator) {
  const headers = deviceCard.locator('button[aria-expanded]')
  for (let i = 0; i < await headers.count(); i++) {
    const header = headers.nth(i)
    if (await header.getAttribute('aria-expanded') === 'false') await header.click()
  }
}

// Start/stop is rendered once per sensor module, so it has to be scoped to the module
// holding the depth toggle - .first() can land on the colour sensor's disabled button.
function depthSensorModule(page: Page): Locator {
  return page.locator('[data-testid="sensor-module"]')
    .filter({ has: page.locator('[data-testid="toggle-stream-depth"]') })
}

async function openFirstDevice(page: Page): Promise<Locator> {
  const deviceCard = page.locator('[data-testid="device-card"]').first()
  await deviceCard.click()
  await expect(page.locator('[title="Loading..."]')).toHaveCount(0, { timeout: 15000 })
  await dismissToasts(page)
  return deviceCard
}

async function startDepthStream(page: Page): Promise<void> {
  const deviceCard = await openFirstDevice(page)
  await expandSensorModules(deviceCard)
  await page.locator('[data-testid="toggle-stream-depth"]').first().check()

  const startButton = depthSensorModule(page).locator('[data-testid="start-streaming"]')
  await expect(startButton).toBeEnabled()
  await startButton.click()
  await expect(page.locator('video.stream-video').first()).toBeVisible({ timeout: 20000 })
}

async function stopDepthStream(page: Page): Promise<void> {
  const stopButton = depthSensorModule(page).locator('[data-testid="stop-streaming"]')
  await stopButton.click()
  await expect(stopButton).toHaveCount(0, { timeout: 15000 })
}

// Opens the metadata overlay of the first tile; frame number and FPS live nowhere else.
async function openMetadataOverlay(page: Page): Promise<Locator> {
  const tile = page.locator('video.stream-video').first().locator('..')
  const toggle = tile.locator('[data-testid="toggle-metadata"]')
  await toggle.waitFor({ state: 'visible', timeout: 20000 })
  await toggle.click()
  return tile
}

// Skip entire file in mock mode
test.beforeEach(async ({ testMode, page }) => {
  test.skip(testMode !== 'real', 'Real device tests require REAL_DEVICE=true')
  await suppressWelcomeModal(page)
})

// A test that fails mid-stream leaves the camera open and the next one cannot start it.
test.afterEach(async ({ testMode, page }) => {
  if (testMode !== 'real') return
  await clickAll(page.locator('[data-testid="stop-streaming"]'))
})

test.describe('@real-device Real Device Tests', () => {
  test.describe('Device Detection', () => {
    test('detects connected RealSense device', async ({ page, getDevices }) => {
      const devices = await getDevices()
      expect(devices.length).toBeGreaterThan(0)
      
      await page.goto('/')

      // Wait for device to appear in UI
      await expect(page.locator('text=/D4[0-9]{2}|Intel RealSense/i').first()).toBeVisible({
        timeout: 15000,
      })
    })

    test('displays correct device information', async ({ page, getDevices }) => {
      const devices = await getDevices()
      const device = devices[0]
      
      await page.goto('/')

      // Check serial number is displayed
      await expect(page.locator(`text=${device.serial_number}`).first()).toBeVisible({ timeout: 10000 })

      // Check firmware version is displayed
      await expect(page.locator(`text=/${device.firmware_version}/`).first()).toBeVisible()
    })
  })

  test.describe('Streaming', () => {
    test('can start and stop depth streaming', async ({ page }) => {
      await page.goto('/')

      await startDepthStream(page)
      await stopDepthStream(page)

      await expect(page.locator('video.stream-video')).toHaveCount(0)
    })

    test('displays depth frames', async ({ page }) => {
      await page.goto('/')

      await startDepthStream(page)
      const tile = await openMetadataOverlay(page)

      // Frame number must keep climbing, and the browser must really decode the frames
      const frameNumber = tile.locator('[data-testid="metadata-frame-number"]')
      const first = Number(await frameNumber.textContent())
      await expect
        .poll(async () => Number(await frameNumber.textContent()), { timeout: 15000 })
        .toBeGreaterThan(first)

      const decoded = await page.locator('video.stream-video').first()
        .evaluate((v: HTMLVideoElement) => v.getVideoPlaybackQuality().totalVideoFrames)
      expect(decoded).toBeGreaterThan(0)

      await stopDepthStream(page)
    })
  })

  test.describe('Sensor Options', () => {
    test('can modify exposure setting', async ({ page, getDevices }) => {
      await page.goto('/')

      const device = (await getDevices())[0]
      const sensorsUrl = `${getApiUrl()}/api/v1/devices/${device.device_id}/sensors/`
      const sensors = await (await fetch(sensorsUrl)).json()
      const sensor = sensors.find((s: SensorInfo) => s.options.some(o => o.option_id === 'exposure'))
      expect(sensor, 'no sensor exposes an exposure control').toBeTruthy()
      const exposure = sensor!.options.find(o => o.option_id === 'exposure')!
      const target = Math.min(exposure.max_value, Math.round(Number(exposure.default_value) * 2))

      const deviceCard = await openFirstDevice(page)
      await expandSensorModules(deviceCard)

      // Scope to the module for the sensor the API gave us, not whichever renders first
      const sensorModule = page.locator('[data-testid="sensor-module"]')
        .filter({ hasText: sensor!.name })
      // A query force-opens the control sections, which are collapsed by default
      await sensorModule.getByPlaceholder('Search controls').fill('exposure')

      // Auto-exposure would make the SDK reject the write and the UI silently revert
      const autoExposure = sensorModule.locator('[data-testid="option-enable_auto_exposure"] input[type="checkbox"]')
      if (await autoExposure.count()) await autoExposure.uncheck()

      const slider = sensorModule.locator('[data-testid="option-exposure"] input[type="range"]')
      await expect(slider).toBeVisible()
      await slider.fill(String(target))
      await slider.dispatchEvent('mouseup')   // the PUT is only sent on mouseup

      await expect(slider).toHaveValue(String(target))
      await expect
        .poll(async () => {
          const url = `${getApiUrl()}/api/v1/devices/${device.device_id}/sensors/${sensor!.sensor_id}/options/exposure/`
          return (await (await fetch(url)).json()).current_value
        }, { timeout: 10000 })
        .toBe(target)
    })
  })

  test.describe('Multi-Camera', () => {
    test('handles multiple cameras if connected', async ({ page, getDevices }) => {
      const devices = await getDevices()
      
      // Skip if only one device
      test.skip(devices.length < 2, 'Need 2+ devices for multi-camera test')
      
      await page.goto('/')

      // Should see multiple device cards
      const deviceCards = page.locator('[data-testid="device-card"]')
      await expect(deviceCards).toHaveCount(devices.length, { timeout: 10000 })

      // Each device serial should be visible
      for (const device of devices) {
        await expect(page.locator(`text=${device.serial_number}`).first()).toBeVisible()
      }
    })
  })
})

test.describe('@real-device Performance Tests', () => {
  test('streaming maintains acceptable frame rate', async ({ page }) => {
    await page.goto('/')

    await startDepthStream(page)
    const tile = await openMetadataOverlay(page)

    // Measured 10-19 fps on an idle bench; 5 only proves frames flow, not throughput.
    const viewerFps = tile.locator('[data-testid="metadata-viewer-fps"]')
    await expect
      .poll(async () => Number(await viewerFps.textContent()), { timeout: 20000 })
      .toBeGreaterThanOrEqual(5)

    console.log(`viewer FPS: ${await viewerFps.textContent()}, hardware FPS: ${await tile.locator('[data-testid="metadata-hardware-fps"]').textContent()}`)

    await stopDepthStream(page)
  })
})
