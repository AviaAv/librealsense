# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2026 RealSense, Inc. All Rights Reserved.

# Raw dual-RGB together with depth, over GMSL (D401) and USB (D401/D405). 60 fps over USB only: the GMSL
# link can't yet carry depth plus both raw colors at 60, so the colors drop frames there.

import pytest
import pyrealsense2 as rs
import pyrsutils as rsutils
from rspy.pytest.device_helpers import require_min_fw_version
import d401_helper as helper
from d401_helper import COLOR0, COLOR1, DEPTH

pytestmark = [pytest.mark.device_each( "D401", "D405" )]


@pytest.fixture( scope="module", autouse=True )
def require_dual_rgb( test_device ):
    dev, _ = test_device
    helper.skip_without_color1( dev )
    _fw['logger'] = dev.as_firmware_logger()   # DIAG


# DIAG: dump the raw FW log (hex) into the test log; parse offline with the FW's HWLogger XML
import logging
log = logging.getLogger( __name__ )
_fw = {}

def drain_fw_log( tag ):
    logger = _fw.get( 'logger' )
    if not logger:
        return
    msg = logger.create_message()
    n = 0
    while n < 20000 and logger.get_firmware_log( msg ):
        log.info( "FWLOG %s ts=%s %s", tag, msg.get_timestamp(), bytes( msg.get_data() ).hex() )
        n += 1
    log.info( "FWLOG %s: %d entries", tag, n )


@pytest.fixture
def depth_sensor( test_device ):
    dev, _ = test_device
    yield dev.first_depth_sensor()


def check_depth_with_both_colors( sensor, w, h, fps=helper.FPS ):
    streams = ((DEPTH, rs.format.z16, 2), (COLOR0, rs.format.rgb8, 3), (COLOR1, rs.format.rgb8, 3))
    profiles = [helper.require_profile( sensor, key, fmt, w, h, fps ) for key, fmt, _ in streams]
    for _ in range( 2 ):   # the second start fails if the first stop left the streams wedged
        drain_fw_log( "before" )
        numbers, sizes = helper.stream( sensor, profiles )
        for key, _, _ in streams:   # DIAG: all counts + frame-number gaps (gap = frame made by camera, lost on host)
            got = numbers.get( key, [] )
            gaps = sum( b - a - 1 for a, b in zip( got, got[1:] ) if b > a + 1 )
            log.info( "DIAG %s %d: %d frames, numbers %s..%s, missing-in-sequence %d", key[0], key[1], len( got ),
                      got[0] if got else None, got[-1] if got else None, gaps )
        drain_fw_log( "after" )
        for key, _, bpp in streams:
            helper.check_rate( numbers, key, fps )
            assert sizes[key] == w * h * bpp, f"{key[0]} {key[1]} frame is {sizes[key]} bytes, expected {w * h * bpp}"


@pytest.mark.context( "nightly" )
def test_depth_with_both_colors( depth_sensor ):
    check_depth_with_both_colors( depth_sensor, 848, 480 )


@pytest.mark.context( "weekly" )
@pytest.mark.parametrize( "w,h", [r for r in helper.RESOLUTIONS if r != (848, 480)] )
def test_depth_with_both_colors_at( depth_sensor, w, h ):
    check_depth_with_both_colors( depth_sensor, w, h )


@pytest.mark.context( "nightly" )
@pytest.mark.device_type( "USB" )
def test_depth_with_both_colors_60fps( test_device, depth_sensor ):
    dev, _ = test_device
    require_min_fw_version( dev, rsutils.version( 5, 17, 5, 15 ), "Depth + both colors at 60 fps" )
    check_depth_with_both_colors( depth_sensor, 848, 480, 60 )
