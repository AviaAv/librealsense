// License: Apache 2.0. See LICENSE file in root directory.
// Copyright(c) 2017 RealSense, Inc. All Rights Reserved.

#pragma once

#include <librealsense2/rs_advanced_mode.hpp>


// Every STxxx group of advanced-mode controls the viewer knows about, each holding the
// value, minimum and maximum firmware reported for its fields.

template<class T>
struct param_group
{
    using group_type = T;
    T vals[3];
    bool update = false;
};

struct advanced_mode_control
{
    param_group<STDepthControlGroup> depth_controls;
    param_group<STRsm> rsm;
    param_group<STRauSupportVectorControl> rsvc;
    param_group<STColorControl> color_control;
    param_group<STRauColorThresholdsControl> rctc;
    param_group<STSloColorThresholdsControl> sctc;
    param_group<STSloPenaltyControl> spc;
    param_group<STHdad> hdad;
    param_group<STColorCorrection> cc;
    param_group<STDepthTableControl> depth_table;
    param_group<STAEControl> ae;
    param_group<STCensusRadius> census;
    param_group<STAFactor> amp_factor;
};

// The advanced-mode values are read from FW in one bulk operation, and only when they went stale
inline void refresh_advanced_mode_controls( rs400::advanced_mode & advanced,
                                            advanced_mode_control & amc,
                                            bool & get_curr_advanced_controls )
{
    if( ! get_curr_advanced_controls )
        return;

    auto all = advanced.get_all_controls();
    for( int k = 0; k < 3; ++k )
    {
        amc.depth_controls.vals[k] = all.depth_control[k];
        amc.rsm.vals[k] = all.rsm[k];
        amc.rsvc.vals[k] = all.rsvc[k];
        amc.color_control.vals[k] = all.color_control[k];
        amc.rctc.vals[k] = all.rctc[k];
        amc.sctc.vals[k] = all.sctc[k];
        amc.spc.vals[k] = all.spc[k];
        amc.cc.vals[k] = all.cc[k];
        amc.depth_table.vals[k] = all.depth_table[k];
        amc.census.vals[k] = all.census[k];
        amc.amp_factor.vals[k] = all.amp_factor[k];
        amc.hdad.vals[k] = all.hdad[k];
        amc.ae.vals[k] = all.ae[k];
    }
    get_curr_advanced_controls = false;
}
