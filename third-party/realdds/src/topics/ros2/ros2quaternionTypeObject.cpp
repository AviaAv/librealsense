// License: Apache 2.0. See LICENSE file in root directory.
// Copyright(c) 2023 Intel Corporation. All Rights Reserved.

/*!
 * @file QuaternionTypeObject.cpp
 * This source file contains the definition of the described types in the IDL file.
 *
 * This file was generated by the tool gen.
 */

#ifdef _WIN32
// Remove linker warning LNK4221 on Visual Studio
namespace { char dummy; }
#endif

#include <realdds/topics/ros2/ros2quaternion.h>
#include "ros2quaternionTypeObject.h"
#include <utility>
#include <sstream>
#include <fastrtps/rtps/common/SerializedPayload.h>
#include <fastrtps/utils/md5.h>
#include <fastrtps/types/TypeObjectFactory.h>
#include <fastrtps/types/TypeNamesGenerator.h>
#include <fastrtps/types/AnnotationParameterValue.h>
#include <fastcdr/FastBuffer.h>
#include <fastcdr/Cdr.h>

using namespace eprosima::fastrtps::rtps;

void registerQuaternionTypes()
{
    TypeObjectFactory *factory = TypeObjectFactory::get_instance();
    factory->add_type_object("geometry_msgs::msg::Quaternion", geometry_msgs::msg::GetQuaternionIdentifier(true),
            geometry_msgs::msg::GetQuaternionObject(true));
    factory->add_type_object("geometry_msgs::msg::Quaternion", geometry_msgs::msg::GetQuaternionIdentifier(false),
            geometry_msgs::msg::GetQuaternionObject(false));



}

namespace geometry_msgs {
    namespace msg {
        const TypeIdentifier* GetQuaternionIdentifier(bool complete)
        {
            const TypeIdentifier * c_identifier = TypeObjectFactory::get_instance()->get_type_identifier("Quaternion", complete);
            if (c_identifier != nullptr && (!complete || c_identifier->_d() == EK_COMPLETE))
            {
                return c_identifier;
            }

            GetQuaternionObject(complete); // Generated inside
            return TypeObjectFactory::get_instance()->get_type_identifier("Quaternion", complete);
        }

        const TypeObject* GetQuaternionObject(bool complete)
        {
            const TypeObject* c_type_object = TypeObjectFactory::get_instance()->get_type_object("Quaternion", complete);
            if (c_type_object != nullptr)
            {
                return c_type_object;
            }
            else if (complete)
            {
                return GetCompleteQuaternionObject();
            }
            //else
            return GetMinimalQuaternionObject();
        }

        const TypeObject* GetMinimalQuaternionObject()
        {
            const TypeObject* c_type_object = TypeObjectFactory::get_instance()->get_type_object("Quaternion", false);
            if (c_type_object != nullptr)
            {
                return c_type_object;
            }

            TypeObject *type_object = new TypeObject();
            type_object->_d(EK_MINIMAL);
            type_object->minimal()._d(TK_STRUCTURE);

            type_object->minimal().struct_type().struct_flags().IS_FINAL(false);
            type_object->minimal().struct_type().struct_flags().IS_APPENDABLE(false);
            type_object->minimal().struct_type().struct_flags().IS_MUTABLE(false);
            type_object->minimal().struct_type().struct_flags().IS_NESTED(false);
            type_object->minimal().struct_type().struct_flags().IS_AUTOID_HASH(false); // Unsupported

            MemberId memberId = 0;
            MinimalStructMember mst_x;
            mst_x.common().member_id(memberId++);
            mst_x.common().member_flags().TRY_CONSTRUCT1(false); // Unsupported
            mst_x.common().member_flags().TRY_CONSTRUCT2(false); // Unsupported
            mst_x.common().member_flags().IS_EXTERNAL(false); // Unsupported
            mst_x.common().member_flags().IS_OPTIONAL(false);
            mst_x.common().member_flags().IS_MUST_UNDERSTAND(false);
            mst_x.common().member_flags().IS_KEY(false);
            mst_x.common().member_flags().IS_DEFAULT(false); // Doesn't apply
            mst_x.common().member_type_id(*TypeObjectFactory::get_instance()->get_type_identifier("double", false));

            MD5 x_hash("x");
            for(int i = 0; i < 4; ++i)
            {
                mst_x.detail().name_hash()[i] = x_hash.digest[i];
            }
            type_object->minimal().struct_type().member_seq().emplace_back(mst_x);

            MinimalStructMember mst_y;
            mst_y.common().member_id(memberId++);
            mst_y.common().member_flags().TRY_CONSTRUCT1(false); // Unsupported
            mst_y.common().member_flags().TRY_CONSTRUCT2(false); // Unsupported
            mst_y.common().member_flags().IS_EXTERNAL(false); // Unsupported
            mst_y.common().member_flags().IS_OPTIONAL(false);
            mst_y.common().member_flags().IS_MUST_UNDERSTAND(false);
            mst_y.common().member_flags().IS_KEY(false);
            mst_y.common().member_flags().IS_DEFAULT(false); // Doesn't apply
            mst_y.common().member_type_id(*TypeObjectFactory::get_instance()->get_type_identifier("double", false));

            MD5 y_hash("y");
            for(int i = 0; i < 4; ++i)
            {
                mst_y.detail().name_hash()[i] = y_hash.digest[i];
            }
            type_object->minimal().struct_type().member_seq().emplace_back(mst_y);

            MinimalStructMember mst_z;
            mst_z.common().member_id(memberId++);
            mst_z.common().member_flags().TRY_CONSTRUCT1(false); // Unsupported
            mst_z.common().member_flags().TRY_CONSTRUCT2(false); // Unsupported
            mst_z.common().member_flags().IS_EXTERNAL(false); // Unsupported
            mst_z.common().member_flags().IS_OPTIONAL(false);
            mst_z.common().member_flags().IS_MUST_UNDERSTAND(false);
            mst_z.common().member_flags().IS_KEY(false);
            mst_z.common().member_flags().IS_DEFAULT(false); // Doesn't apply
            mst_z.common().member_type_id(*TypeObjectFactory::get_instance()->get_type_identifier("double", false));

            MD5 z_hash("z");
            for(int i = 0; i < 4; ++i)
            {
                mst_z.detail().name_hash()[i] = z_hash.digest[i];
            }
            type_object->minimal().struct_type().member_seq().emplace_back(mst_z);

            MinimalStructMember mst_w;
            mst_w.common().member_id(memberId++);
            mst_w.common().member_flags().TRY_CONSTRUCT1(false); // Unsupported
            mst_w.common().member_flags().TRY_CONSTRUCT2(false); // Unsupported
            mst_w.common().member_flags().IS_EXTERNAL(false); // Unsupported
            mst_w.common().member_flags().IS_OPTIONAL(false);
            mst_w.common().member_flags().IS_MUST_UNDERSTAND(false);
            mst_w.common().member_flags().IS_KEY(false);
            mst_w.common().member_flags().IS_DEFAULT(false); // Doesn't apply
            mst_w.common().member_type_id(*TypeObjectFactory::get_instance()->get_type_identifier("double", false));

            MD5 w_hash("w");
            for(int i = 0; i < 4; ++i)
            {
                mst_w.detail().name_hash()[i] = w_hash.digest[i];
            }
            type_object->minimal().struct_type().member_seq().emplace_back(mst_w);


            // Header
            // TODO Inheritance
            //type_object->minimal().struct_type().header().base_type()._d(EK_MINIMAL);
            //type_object->minimal().struct_type().header().base_type().equivalence_hash()[0..13];

            TypeIdentifier identifier;
            identifier._d(EK_MINIMAL);

            SerializedPayload_t payload(static_cast<uint32_t>(
                MinimalStructType::getCdrSerializedSize(type_object->minimal().struct_type()) + 4));
            eprosima::fastcdr::FastBuffer fastbuffer((char*) payload.data, payload.max_size);
            // Fixed endian (Page 221, EquivalenceHash definition of Extensible and Dynamic Topic Types for DDS document)
            eprosima::fastcdr::Cdr ser(
                fastbuffer, eprosima::fastcdr::Cdr::LITTLE_ENDIANNESS,
                eprosima::fastcdr::Cdr::DDS_CDR); // Object that serializes the data.
            payload.encapsulation = CDR_LE;

            type_object->serialize(ser);
            payload.length = (uint32_t)ser.getSerializedDataLength(); //Get the serialized length
            MD5 objectHash;
            objectHash.update((char*)payload.data, payload.length);
            objectHash.finalize();
            for(int i = 0; i < 14; ++i)
            {
                identifier.equivalence_hash()[i] = objectHash.digest[i];
            }

            TypeObjectFactory::get_instance()->add_type_object("Quaternion", &identifier, type_object);
            delete type_object;
            return TypeObjectFactory::get_instance()->get_type_object("Quaternion", false);
        }

        const TypeObject* GetCompleteQuaternionObject()
        {
            const TypeObject* c_type_object = TypeObjectFactory::get_instance()->get_type_object("Quaternion", true);
            if (c_type_object != nullptr && c_type_object->_d() == EK_COMPLETE)
            {
                return c_type_object;
            }

            TypeObject *type_object = new TypeObject();
            type_object->_d(EK_COMPLETE);
            type_object->complete()._d(TK_STRUCTURE);

            type_object->complete().struct_type().struct_flags().IS_FINAL(false);
            type_object->complete().struct_type().struct_flags().IS_APPENDABLE(false);
            type_object->complete().struct_type().struct_flags().IS_MUTABLE(false);
            type_object->complete().struct_type().struct_flags().IS_NESTED(false);
            type_object->complete().struct_type().struct_flags().IS_AUTOID_HASH(false); // Unsupported

            MemberId memberId = 0;
            CompleteStructMember cst_x;
            cst_x.common().member_id(memberId++);
            cst_x.common().member_flags().TRY_CONSTRUCT1(false); // Unsupported
            cst_x.common().member_flags().TRY_CONSTRUCT2(false); // Unsupported
            cst_x.common().member_flags().IS_EXTERNAL(false); // Unsupported
            cst_x.common().member_flags().IS_OPTIONAL(false);
            cst_x.common().member_flags().IS_MUST_UNDERSTAND(false);
            cst_x.common().member_flags().IS_KEY(false);
            cst_x.common().member_flags().IS_DEFAULT(false); // Doesn't apply
            cst_x.common().member_type_id(*TypeObjectFactory::get_instance()->get_type_identifier("double", false));

            cst_x.detail().name("x");

            type_object->complete().struct_type().member_seq().emplace_back(cst_x);

            CompleteStructMember cst_y;
            cst_y.common().member_id(memberId++);
            cst_y.common().member_flags().TRY_CONSTRUCT1(false); // Unsupported
            cst_y.common().member_flags().TRY_CONSTRUCT2(false); // Unsupported
            cst_y.common().member_flags().IS_EXTERNAL(false); // Unsupported
            cst_y.common().member_flags().IS_OPTIONAL(false);
            cst_y.common().member_flags().IS_MUST_UNDERSTAND(false);
            cst_y.common().member_flags().IS_KEY(false);
            cst_y.common().member_flags().IS_DEFAULT(false); // Doesn't apply
            cst_y.common().member_type_id(*TypeObjectFactory::get_instance()->get_type_identifier("double", false));

            cst_y.detail().name("y");

            type_object->complete().struct_type().member_seq().emplace_back(cst_y);

            CompleteStructMember cst_z;
            cst_z.common().member_id(memberId++);
            cst_z.common().member_flags().TRY_CONSTRUCT1(false); // Unsupported
            cst_z.common().member_flags().TRY_CONSTRUCT2(false); // Unsupported
            cst_z.common().member_flags().IS_EXTERNAL(false); // Unsupported
            cst_z.common().member_flags().IS_OPTIONAL(false);
            cst_z.common().member_flags().IS_MUST_UNDERSTAND(false);
            cst_z.common().member_flags().IS_KEY(false);
            cst_z.common().member_flags().IS_DEFAULT(false); // Doesn't apply
            cst_z.common().member_type_id(*TypeObjectFactory::get_instance()->get_type_identifier("double", false));

            cst_z.detail().name("z");

            type_object->complete().struct_type().member_seq().emplace_back(cst_z);

            CompleteStructMember cst_w;
            cst_w.common().member_id(memberId++);
            cst_w.common().member_flags().TRY_CONSTRUCT1(false); // Unsupported
            cst_w.common().member_flags().TRY_CONSTRUCT2(false); // Unsupported
            cst_w.common().member_flags().IS_EXTERNAL(false); // Unsupported
            cst_w.common().member_flags().IS_OPTIONAL(false);
            cst_w.common().member_flags().IS_MUST_UNDERSTAND(false);
            cst_w.common().member_flags().IS_KEY(false);
            cst_w.common().member_flags().IS_DEFAULT(false); // Doesn't apply
            cst_w.common().member_type_id(*TypeObjectFactory::get_instance()->get_type_identifier("double", false));

            cst_w.detail().name("w");

            type_object->complete().struct_type().member_seq().emplace_back(cst_w);


            // Header
            type_object->complete().struct_type().header().detail().type_name("Quaternion");
            // TODO inheritance


            TypeIdentifier identifier;
            identifier._d(EK_COMPLETE);

            SerializedPayload_t payload(static_cast<uint32_t>(
                CompleteStructType::getCdrSerializedSize(type_object->complete().struct_type()) + 4));
            eprosima::fastcdr::FastBuffer fastbuffer((char*) payload.data, payload.max_size);
            // Fixed endian (Page 221, EquivalenceHash definition of Extensible and Dynamic Topic Types for DDS document)
            eprosima::fastcdr::Cdr ser(
                fastbuffer, eprosima::fastcdr::Cdr::LITTLE_ENDIANNESS,
                eprosima::fastcdr::Cdr::DDS_CDR); // Object that serializes the data.
            payload.encapsulation = CDR_LE;

            type_object->serialize(ser);
            payload.length = (uint32_t)ser.getSerializedDataLength(); //Get the serialized length
            MD5 objectHash;
            objectHash.update((char*)payload.data, payload.length);
            objectHash.finalize();
            for(int i = 0; i < 14; ++i)
            {
                identifier.equivalence_hash()[i] = objectHash.digest[i];
            }

            TypeObjectFactory::get_instance()->add_type_object("Quaternion", &identifier, type_object);
            delete type_object;
            return TypeObjectFactory::get_instance()->get_type_object("Quaternion", true);
        }

    } // namespace msg
} // namespace geometry_msgs