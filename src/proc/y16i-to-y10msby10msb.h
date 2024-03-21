// License: Apache 2.0. See LICENSE file in root directory.
// Copyright(c) 2022 Intel Corporation. All Rights Reserved.

#pragma once

#include "synthetic-stream.h"
#include "image.h"

namespace librealsense
{
    class y16i_to_y10msby10msb : public interleaved_functional_processing_block
    {
    public:
        y16i_to_y10msby10msb(int left_idx = 1, int right_idx = 2);

    protected:
        y16i_to_y10msby10msb(const char* name, int left_idx, int right_idx);
        void process_function( uint8_t * const dest[], const uint8_t * source, int width, int height, int actual_size, int input_size) override;
    };
}

