// License: Apache 2.0. See LICENSE file in root directory.
// Copyright(c) 2017 RealSense, Inc. All Rights Reserved.

#pragma once

#include "advanced-mode-model.h"
#include "control-section.h"
#include "textual-icons.h"

#include <realsense_imgui.h>
#include <rsutils/string/string-utilities.h>

#include <map>
#include <memory>
#include <sstream>
#include <string>
#include <type_traits>


template<class T>
bool* draw_edit_button(const char* id, T val, std::string*& val_str)
{
    static std::map<const char*, bool> edit_mode;
    static std::map<const char*, std::string> edit_value;

    ImGui::SameLine();
    ImGui::SetCursorPosX(268);
    if (!edit_mode[id])
    {
        std::string edit_id = rsutils::string::from() 
            << rs2::textual_icons::edit << "##" << id;
        ImGui::PushStyleColor(ImGuiCol_Text,  { 0.8f, 0.8f, 0.8f, 1.f });
        ImGui::PushStyleColor(ImGuiCol_TextSelectedBg, { 0.8f, 0.8f, 0.8f, 1.f } );
        ImGui::PushStyleColor(ImGuiCol_ButtonHovered, { 1.f,1.f,1.f,0.f });
        ImGui::PushStyleColor(ImGuiCol_Button, { 1.f,1.f,1.f,0.f });
        if (ImGui::Button(edit_id.c_str(), { 20, 20 }))
        {
            edit_value[id] = rsutils::string::from( val );
            edit_mode[id] = true;
        }
        if (ImGui::IsItemHovered())
        {
            RsImGui::CustomTooltip("Enter text-edit mode");
        }
        ImGui::PopStyleColor(4);
    }
    else
    {
        std::string edit_id = rsutils::string::from()   
            << rs2::textual_icons::edit << "##" << id;
        ImGui::PushStyleColor(ImGuiCol_Text,  { 0.8f, 0.8f, 1.f, 1.f });
        ImGui::PushStyleColor(ImGuiCol_TextSelectedBg,  { 0.8f, 0.8f, 1.f, 1.f });
        ImGui::PushStyleColor(ImGuiCol_ButtonHovered, { 1.f,1.f,1.f,0.f });
        ImGui::PushStyleColor(ImGuiCol_Button, { 1.f,1.f,1.f,0.f });
        if (ImGui::Button(edit_id.c_str(), { 20, 20 }))
        {
            edit_mode[id] = false;
        }
        if (ImGui::IsItemHovered())
        {
            RsImGui::CustomTooltip("Exit text-edit mode");
        }
        ImGui::PopStyleColor(4);
    }

    val_str = &edit_value[id];
    return &edit_mode[id];
}

// One slider for every advanced-mode field. A whole-number field gets the same integer widget
// an integer option gets; the rest get the float one. Both share the text-edit box beside them,
// and the range check that lets you type into a control firmware has pinned to a single value.
template<class T, class S>
inline void slider(std::string& error_message, const char* id, T* val, S T::* field, bool& to_set)
{
    bool const whole = std::is_integral< S >::value;
    double const min = (double)((val + 1)->*field);
    double const max = (double)((val + 2)->*field);

    ImGui::Text("%s", id);

    std::string* val_ptr;
    auto edit_mode = draw_edit_button(id, val->*field, val_ptr);
    std::string const slider_id = rsutils::string::from() << "##" << id;

    if (*edit_mode)
    {
        char buff[TEXT_BUFF_SIZE];
        memset(buff, 0, TEXT_BUFF_SIZE);
        strncpy(buff, val_ptr->c_str(), TEXT_BUFF_SIZE - 1);
        if (ImGui::InputText(slider_id.c_str(), buff, TEXT_BUFF_SIZE,
            ImGuiInputTextFlags_EnterReturnsTrue))
        {
            double new_value = 0.;
            bool parsed;
            if (whole)
            {
                int i = 0;
                parsed = rsutils::string::string_to_value<int>(buff, i);
                new_value = i;
            }
            else
            {
                float f = 0.f;
                parsed = rsutils::string::string_to_value<float>(buff, f);
                new_value = f;
            }

            if (!parsed)
            {
                error_message = whole ? "Invalid integer input!" : "Invalid numeric input!";
            }
            // min != max steps over this check for the controls whose min and max firmware has
            // set equal to the actual value
            else if ((min != max) && ((new_value > max) || (new_value < min)))
            {
                std::stringstream ss;
                ss << "New value " << new_value << " must be within [" << min << ", " << max << "] range";
                error_message = ss.str();
            }
            else
            {
                val->*field = static_cast<S>(new_value);
                to_set = true;
            }

            *edit_mode = false;
        }
        *val_ptr = buff;
    }
    else if (whole)
    {
        int temp = (int)(val->*field);
        if (RsImGui::SliderIntWithSteps(slider_id.c_str(), &temp, (int)min, (int)max, 1))
        {
            val->*field = static_cast<S>(temp);
            to_set = true;
        }
    }
    else
    {
        float temp = (float)(val->*field);
        if (ImGui::SliderFloat(slider_id.c_str(), &temp, (float)min, (float)max))
        {
            val->*field = static_cast<S>(temp);
            to_set = true;
        }
    }
}
template<class T, class S>
inline void checkbox(const char* id, T* val, S T::* f, bool& to_set)
{
    bool temp = (val->*f) > 0;

    if (ImGui::Checkbox(id, &temp))
    {
        val->*f = temp ? 1 : 0;
        to_set = true;
    }
}


// One advanced-mode control: a named field of an STxxx struct, whose value, minimum and
// maximum are vals[0..2]. Which widget suits it is not the call site's business - the range
// firmware reported answers it, by the same rule option_model::is_checkbox() uses. Firmware
// reports no step for these, so the field's own type stands in: a whole-number field cannot
// hold anything between 0 and 1, which is what step==1 tells you about an option.
template< class T, class S >
class advanced_control : public rs2::control_model
{
public:
    advanced_control( const char * name, param_group< T > & group, S T::* field )
        : _name( name ), _group( &group ), _field( field )
    {
    }

    std::string const & name() const override { return _name; }
    void draw( rs2::control_draw_context & ctx ) override
    {
        T * const vals = _group->vals;
        bool to_set = false;

        if( std::is_integral< S >::value
            && ( vals + 1 )->*_field == 0 && ( vals + 2 )->*_field <= 1 )
            checkbox( _name.c_str(), vals, _field, to_set );
        else
            slider( ctx.error_message, _name.c_str(), vals, _field, to_set );

        if( to_set )
            ctx.changed = true;
    }

private:
    std::string _name;
    param_group< T > * _group;
    S T::* _field;
};

template< class T, class S >
inline void add_control( rs2::control_section & section,
                         const char * name, param_group< T > & group, S T::* field )
{
    section.add( std::unique_ptr< rs2::control_model >(
        new advanced_control< T, S >( name, group, field ) ) );
}

// A section writes its group back to FW once, after the controls inside it have drawn; a rejected
// write puts the value the camera still holds back on screen and surfaces the error
template< class Set, class Revert >
inline rs2::control_section & add_advanced_section( rs2::control_section & parent, const char * title,
                                                    bool & was_set, Set set, Revert revert )
{
    auto & section = parent.add_section( title, title );
    section.gap_above = false;
    section.on_open = []() { ImGui::PushItemWidth( ImGui::CalcItemWidth() ); };
    section.on_close = [&was_set, set, revert]( rs2::control_draw_context & ctx )
    {
        ImGui::PopItemWidth();
        if( ! ctx.changed )
            return;
        try
        {
            set();
        }
        catch( ... )
        {
            revert();
            throw;
        }
        was_set = true;
    };
    return section;
}

// The 13 groups of advanced-mode controls, as sections of named controls. Nothing is drawn here -
// control_section::draw() decides what the current search leaves visible.
inline void build_advanced_mode_sections( rs2::control_section & root,
                                          rs400::advanced_mode & advanced,
                                          advanced_mode_control & amc,
                                          bool & was_set,
                                          bool ae_setpoint_unsupported = false )
{
    {
        auto & s = add_advanced_section( root, "Depth Control", was_set,
            [&]() { advanced.set_depth_control( amc.depth_controls.vals[0] ); },
            [&]() { amc.depth_controls.vals[0] = advanced.get_depth_control( 0 ); } );
        add_control( s, "DS Second Peak Threshold", amc.depth_controls, &STDepthControlGroup::deepSeaSecondPeakThreshold );
        add_control( s, "DS Neighbor Threshold", amc.depth_controls, &STDepthControlGroup::deepSeaNeighborThreshold );
        add_control( s, "DS Median Threshold", amc.depth_controls, &STDepthControlGroup::deepSeaMedianThreshold );
        add_control( s, "Estimate Median Increment", amc.depth_controls, &STDepthControlGroup::plusIncrement );
        add_control( s, "Estimate Median Decrement", amc.depth_controls, &STDepthControlGroup::minusDecrement );
        add_control( s, "Score Minimum Threshold", amc.depth_controls, &STDepthControlGroup::scoreThreshA );
        add_control( s, "Score Maximum Threshold", amc.depth_controls, &STDepthControlGroup::scoreThreshB );
        add_control( s, "DS LR Threshold", amc.depth_controls, &STDepthControlGroup::lrAgreeThreshold );
        add_control( s, "Texture Count Threshold", amc.depth_controls, &STDepthControlGroup::textureCountThreshold );
        add_control( s, "Texture Difference Threshold", amc.depth_controls, &STDepthControlGroup::textureDifferenceThreshold );
    }
    {
        auto & s = add_advanced_section( root, "Rsm", was_set,
            [&]() { advanced.set_rsm( amc.rsm.vals[0] ); },
            [&]() { amc.rsm.vals[0] = advanced.get_rsm( 0 ); } );
        add_control( s, "RSM Bypass", amc.rsm, &STRsm::rsmBypass );
        add_control( s, "Disparity Difference Threshold", amc.rsm, &STRsm::diffThresh );
        add_control( s, "SLO RAU Difference Threshold", amc.rsm, &STRsm::sloRauDiffThresh );
        add_control( s, "Remove Threshold", amc.rsm, &STRsm::removeThresh );
    }
    {
        auto & s = add_advanced_section( root, "Rau Support Vector Control", was_set,
            [&]() { advanced.set_rau_support_vector_control( amc.rsvc.vals[0] ); },
            [&]() { amc.rsvc.vals[0] = advanced.get_rau_support_vector_control( 0 ); } );
        add_control( s, "Min West", amc.rsvc, &STRauSupportVectorControl::minWest );
        add_control( s, "Min East", amc.rsvc, &STRauSupportVectorControl::minEast );
        add_control( s, "Min WE Sum", amc.rsvc, &STRauSupportVectorControl::minWEsum );
        add_control( s, "Min North", amc.rsvc, &STRauSupportVectorControl::minNorth );
        add_control( s, "Min South", amc.rsvc, &STRauSupportVectorControl::minSouth );
        add_control( s, "Min NS Sum", amc.rsvc, &STRauSupportVectorControl::minNSsum );
        add_control( s, "U Shrink", amc.rsvc, &STRauSupportVectorControl::uShrink );
        add_control( s, "V Shrink", amc.rsvc, &STRauSupportVectorControl::vShrink );
    }
    {
        auto & s = add_advanced_section( root, "Color Control", was_set,
            [&]() { advanced.set_color_control( amc.color_control.vals[0] ); },
            [&]() { amc.color_control.vals[0] = advanced.get_color_control( 0 ); } );
        add_control( s, "Disable SAD Color", amc.color_control, &STColorControl::disableSADColor );
        add_control( s, "Disable RAU Color", amc.color_control, &STColorControl::disableRAUColor );
        add_control( s, "Disable SLO Right Color", amc.color_control, &STColorControl::disableSLORightColor );
        add_control( s, "Disable SLO Left Color", amc.color_control, &STColorControl::disableSLOLeftColor );
        add_control( s, "Disable SAD Normalize", amc.color_control, &STColorControl::disableSADNormalize );
    }
    {
        auto & s = add_advanced_section( root, "Rau Color Thresholds Control", was_set,
            [&]() { advanced.set_rau_thresholds_control( amc.rctc.vals[0] ); },
            [&]() { amc.rctc.vals[0] = advanced.get_rau_thresholds_control( 0 ); } );
        add_control( s, "Diff Threshold Red", amc.rctc, &STRauColorThresholdsControl::rauDiffThresholdRed );
        add_control( s, "Diff Threshold Green", amc.rctc, &STRauColorThresholdsControl::rauDiffThresholdGreen );
        add_control( s, "Diff Threshold Blue", amc.rctc, &STRauColorThresholdsControl::rauDiffThresholdBlue );
    }
    {
        auto & s = add_advanced_section( root, "SLO Color Thresholds Control", was_set,
            [&]() { advanced.set_slo_color_thresholds_control( amc.sctc.vals[0] ); },
            [&]() { amc.sctc.vals[0] = advanced.get_slo_color_thresholds_control( 0 ); } );
        add_control( s, "Diff Threshold Red", amc.sctc, &STSloColorThresholdsControl::diffThresholdRed );
        add_control( s, "Diff Threshold Green", amc.sctc, &STSloColorThresholdsControl::diffThresholdGreen );
        add_control( s, "Diff Threshold Blue", amc.sctc, &STSloColorThresholdsControl::diffThresholdBlue );
    }
    {
        auto & s = add_advanced_section( root, "SLO Penalty Control", was_set,
            [&]() { advanced.set_slo_penalty_control( amc.spc.vals[0] ); },
            [&]() { amc.spc.vals[0] = advanced.get_slo_penalty_control( 0 ); } );
        add_control( s, "K1 Penalty", amc.spc, &STSloPenaltyControl::sloK1Penalty );
        add_control( s, "K2 Penalty", amc.spc, &STSloPenaltyControl::sloK2Penalty );
        add_control( s, "K1 Penalty Mod1", amc.spc, &STSloPenaltyControl::sloK1PenaltyMod1 );
        add_control( s, "K1 Penalty Mod2", amc.spc, &STSloPenaltyControl::sloK1PenaltyMod2 );
        add_control( s, "K2 Penalty Mod1", amc.spc, &STSloPenaltyControl::sloK2PenaltyMod1 );
        add_control( s, "K2 Penalty Mod2", amc.spc, &STSloPenaltyControl::sloK2PenaltyMod2 );
    }
    {
        auto & s = add_advanced_section( root, "HDAD", was_set,
            [&]() { advanced.set_hdad( amc.hdad.vals[0] ); },
            [&]() { amc.hdad.vals[0] = advanced.get_hdad(); } );
        add_control( s, "Ignore SAD", amc.hdad, &STHdad::ignoreSAD );
        add_control( s, "AD Lambda", amc.hdad, &STHdad::lambdaAD );
        add_control( s, "Census Lambda", amc.hdad, &STHdad::lambdaCensus );
    }
    {
        auto & s = add_advanced_section( root, "Color Correction", was_set,
            [&]() { advanced.set_color_correction( amc.cc.vals[0] ); },
            [&]() { amc.cc.vals[0] = advanced.get_color_correction( 0 ); } );
        add_control( s, "Color Correction 1", amc.cc, &STColorCorrection::colorCorrection1 );
        add_control( s, "Color Correction 2", amc.cc, &STColorCorrection::colorCorrection2 );
        add_control( s, "Color Correction 3", amc.cc, &STColorCorrection::colorCorrection3 );
        add_control( s, "Color Correction 4", amc.cc, &STColorCorrection::colorCorrection4 );
        add_control( s, "Color Correction 5", amc.cc, &STColorCorrection::colorCorrection5 );
        add_control( s, "Color Correction 6", amc.cc, &STColorCorrection::colorCorrection6 );
        add_control( s, "Color Correction 7", amc.cc, &STColorCorrection::colorCorrection7 );
        add_control( s, "Color Correction 8", amc.cc, &STColorCorrection::colorCorrection8 );
        add_control( s, "Color Correction 9", amc.cc, &STColorCorrection::colorCorrection9 );
        add_control( s, "Color Correction 10", amc.cc, &STColorCorrection::colorCorrection10 );
        add_control( s, "Color Correction 11", amc.cc, &STColorCorrection::colorCorrection11 );
        add_control( s, "Color Correction 12", amc.cc, &STColorCorrection::colorCorrection12 );
    }
    {
        auto & s = add_advanced_section( root, "Depth Table", was_set,
            [&]() { advanced.set_depth_table( amc.depth_table.vals[0] ); },
            [&]() { amc.depth_table.vals[0] = advanced.get_depth_table( 0 ); } );
        add_control( s, "Depth Units", amc.depth_table, &STDepthTableControl::depthUnits );
        add_control( s, "Depth Clamp Min", amc.depth_table, &STDepthTableControl::depthClampMin );
        add_control( s, "Depth Clamp Max", amc.depth_table, &STDepthTableControl::depthClampMax );
        add_control( s, "Disparity Mode", amc.depth_table, &STDepthTableControl::disparityMode );
        add_control( s, "Disparity Shift", amc.depth_table, &STDepthTableControl::disparityShift );
    }
    if( ! ae_setpoint_unsupported )   // D457 and the D500 family have no AE set point
    {
        auto & s = add_advanced_section( root, "AE Control", was_set,
            [&]() { advanced.set_ae_control( amc.ae.vals[0] ); },
            [&]() { amc.ae.vals[0] = advanced.get_ae_control(); } );
        add_control( s, "Mean Intensity Set Point", amc.ae, &STAEControl::meanIntensitySetPoint );
    }
    {
        auto & s = add_advanced_section( root, "Census Enable Reg", was_set,
            [&]() { advanced.set_census( amc.census.vals[0] ); },
            [&]() { amc.census.vals[0] = advanced.get_census( 0 ); } );
        add_control( s, "u-Diameter", amc.census, &STCensusRadius::uDiameter );
        add_control( s, "v-Diameter", amc.census, &STCensusRadius::vDiameter );
    }
    {
        auto & s = add_advanced_section( root, "Disparity Modulation", was_set,
            [&]() { advanced.set_amp_factor( amc.amp_factor.vals[0] ); },
            [&]() { amc.amp_factor.vals[0] = advanced.get_amp_factor( 0 ); } );
        add_control( s, "A Factor", amc.amp_factor, &STAFactor::amplitude );
    }
}
