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


#if !defined(FIT_SET_MESG_LISTENER_HPP)
#define FIT_SET_MESG_LISTENER_HPP

#include "fit_set_mesg.hpp"

namespace fit
{

class SetMesgListener
{
public:
    virtual ~SetMesgListener() {}
    virtual void OnMesg(SetMesg& mesg) = 0;
};

} // namespace fit

#endif // !defined(FIT_SET_MESG_LISTENER_HPP)
