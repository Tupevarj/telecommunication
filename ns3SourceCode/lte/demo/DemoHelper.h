/*
 * DemoHelper.h
 *
 *  Created on: 12.12.2017
 *      Author: tupevarj
 */

#pragma once
#include <ns3/lte-module.h>
#include <ns3/core-module.h>
#include <ns3/network-module.h>
#include <ns3/mobility-module.h>
#include <ns3/internet-module.h>
#include <ns3/config-store-module.h>
#include <ns3/buildings-module.h>
#include <ns3/point-to-point-helper.h>
#include <ns3/applications-module.h>
#include <ns3/log.h>

using namespace ns3;

class DemoHelper
{
public:
//	static void CreateHexagonalTopology(uint32_t nEnbs, uint32_t nEnbsX, double interSiteDistance);
	static void CreateHexagonalTopology(Ptr<PointToPointEpcHelper>& epcHelper, MobilityHelper& mobility, Box& macroUeBox, Ptr <LteHelper> lteHelper, uint32_t nEnbs, uint32_t nEnbsX, double interSiteDistance, bool epc, double enbsTx, uint16_t enbEARFCN, uint16_t enbBandwidth);
	static void CreateUsers(NodeContainer& macroUes, MobilityHelper& mobility, Box& macroUeBox, Ptr <LteHelper> lteHelper, uint32_t nUes, double uesSpeed);
	static void CreateEPC(Ptr<PointToPointEpcHelper>& epcHelper, Ptr <LteHelper> lteHelper, NodeContainer& macroUes, bool useUdp, bool epcDl, bool epcUl, uint16_t nBearersPerUe);
	static void NoEPC();
};
