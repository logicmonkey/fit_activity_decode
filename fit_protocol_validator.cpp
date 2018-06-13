////////////////////////////////////////////////////////////////////////////////
// The following FIT Protocol software provided may be used with FIT protocol
// devices only and remains the copyrighted property of Dynastream Innovations Inc.
// The software is being provided on an "as-is" basis and as an accommodation,
// and therefore all warranties, representations, or guarantees of any kind
// (whether express, implied or statutory) including, without limitation,
// warranties of merchantability, non-infringement, or fitness for a particular
// purpose, are specifically disclaimed.
//
// Copyright 2018 Dynastream Innovations Inc.
////////////////////////////////////////////////////////////////////////////////
// ****WARNING****  This file is auto-generated!  Do NOT edit this file.
// Profile Version = 20.64Release
// Tag = production/akw/20.64.00-0-g97c95ef
////////////////////////////////////////////////////////////////////////////////


#include "fit_mesg.hpp"
#include "fit_mesg_definition.hpp"
#include "fit_protocol_validator.hpp"

fit::ProtocolValidator::ProtocolValidator( ProtocolVersion version )
    : validator( nullptr )
{
    switch ( version )
    {
    case ProtocolVersion::V10:
        validator = new V1Validator();
        break;

    case ProtocolVersion::V20:
    default:
        break;
    }
}

fit::ProtocolValidator::~ProtocolValidator()
{
    if ( nullptr != validator )
    {
        delete validator;
    }
}

bool fit::ProtocolValidator::ValidateMesg( const Mesg& mesg )
{
    if ( nullptr == validator ) return true;
    return validator->ValidateMesg( mesg );
}

bool fit::ProtocolValidator::ValidateMesgDefn( const MesgDefinition& defn )
{
    if ( nullptr == validator ) return true;
    return validator->ValidateMesgDefn( defn );
}

bool fit::V1Validator::ValidateMesg( const Mesg& mesg )
{
    if ( mesg.GetDeveloperFields().size() != 0 )
    {
        return false;
    }

    for ( FIT_UINT16 i = 0; i < mesg.GetNumFields(); i++ )
    {
        const Field* fld = mesg.GetFieldByIndex( i );
        FIT_UINT8 typeNum = fld->GetType() & FIT_BASE_TYPE_NUM_MASK;

        // V2 introduces 64 bit types.
        if ( typeNum > ( FIT_BASE_TYPE_BYTE & FIT_BASE_TYPE_NUM_MASK ) )
        {
            return false;
        }
    }

    return true;
}

bool fit::V1Validator::ValidateMesgDefn( const MesgDefinition& defn )
{
    if ( defn.GetDevFields().size() != 0 )
    {
        return false;
    }

    for ( auto fld : defn.GetFields() )
    {
        FIT_UINT8 typeNum = fld.GetType() & FIT_BASE_TYPE_NUM_MASK;

        // V2 introduces 64 bit types.
        if ( typeNum > ( FIT_BASE_TYPE_BYTE & FIT_BASE_TYPE_NUM_MASK ) )
        {
            return false;
        }
    }

    return true;
}

