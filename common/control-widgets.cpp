// License: Apache 2.0. See LICENSE file in root directory.
// Copyright(c) 2026 RealSense, Inc. All Rights Reserved.

#include "control-widgets.h"
#include "device-model.h"   // the palette
#include "textual-icons.h"

#include <realsense_imgui.h>
#include <rsutils/string/from.h>


namespace rs2 {


void draw_edit_toggle( std::string const & id,
                       float cursor_x,
                       bool & edit_mode,
                       std::string & edit_value,
                       std::string const & value_now )
{
    ImGui::SameLine();
    ImGui::SetCursorPosX( cursor_x );

    std::string const edit_id = rsutils::string::from() << textual_icons::edit << "##" << id;
    ImGui::PushStyleColor( ImGuiCol_Text, edit_mode ? light_blue : light_grey );
    ImGui::PushStyleColor( ImGuiCol_TextSelectedBg, edit_mode ? light_blue : light_grey );
    ImGui::PushStyleColor( ImGuiCol_ButtonHovered, { 1.f, 1.f, 1.f, 0.f } );
    ImGui::PushStyleColor( ImGuiCol_Button, { 1.f, 1.f, 1.f, 0.f } );

    if( ImGui::Button( edit_id.c_str(), { 20, 20 } ) )
    {
        if( ! edit_mode )
            edit_value = value_now;
        edit_mode = ! edit_mode;
    }
    if( ImGui::IsItemHovered() )
        RsImGui::CustomTooltip( edit_mode ? "Exit text-edit mode" : "Enter text-edit mode" );

    ImGui::PopStyleColor( 4 );
}


}  // namespace rs2
