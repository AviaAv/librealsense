// License: Apache 2.0. See LICENSE file in root directory.
// Copyright(c) 2026 RealSense, Inc. All Rights Reserved.

#pragma once

#include <string>


namespace rs2 {


// The pencil beside a control that swaps its slider for a text box, and back. Both the sensor
// options and the advanced-mode controls offer it, so it is drawn in one place: cursor_x is where
// the icon goes, value_now seeds the box with what the control reads right now.
void draw_edit_toggle( std::string const & id,
                       float cursor_x,
                       bool & edit_mode,
                       std::string & edit_value,
                       std::string const & value_now );


}  // namespace rs2
