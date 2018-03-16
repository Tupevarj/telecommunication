/*
 * DemoHelper.cc
 *
 *  Created on: 12.12.2017
 *      Author: tupevarj
 */

#include "DemoHelper.h"

using namespace ns3;

void
DemoHelper::CreateHexagonalTopology(Ptr<PointToPointEpcHelper>& epcHelper, MobilityHelper& mobility, Box& macroUeBox, Ptr <LteHelper> lteHelper, uint32_t nEnbs, uint32_t nEnbsX, double interSiteDistance,
									bool epc, double enbsTx, uint16_t enbEARFCN, uint16_t enbBandwidth)
{

	//////////////////////////////////////////////////////////////////
	// MACRO UE BOX
	//////////////////////////////////////////////////////////////////

	double areaMarginFactor = 0.5;

	if (nEnbs > 0)
	{
	    uint32_t currentSite = nEnbs -1;
	    uint32_t biRowIndex = (currentSite / (nEnbsX + nEnbsX + 1));
	    uint32_t biRowRemainder = currentSite % (nEnbsX + nEnbsX + 1);
	    uint32_t rowIndex = biRowIndex*2 + 1;
	    if (biRowRemainder >= nEnbsX)
	    {
	        ++rowIndex;
	    }
	    uint32_t nMacroEnbSitesY = rowIndex;

	    macroUeBox = Box (-areaMarginFactor*interSiteDistance, (nEnbsX + areaMarginFactor)*interSiteDistance, -areaMarginFactor*interSiteDistance,
	                      (nMacroEnbSitesY -1)*interSiteDistance*sqrt (0.75) + areaMarginFactor*interSiteDistance, 1.5, 1.5);
	  }
	else
	{
		macroUeBox = Box (0, 150, 0, 150, 1.5, 1.5);
	}


	//////////////////////////////////////////////////////////////////
	// ENBS
	//////////////////////////////////////////////////////////////////

	NodeContainer macroEnbs;
	macroEnbs.Create (3 * nEnbs);

	mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");


	lteHelper->SetAttribute("PathlossModel", StringValue("ns3::FriisPropagationLossModel"));
//	  lteHelper->SetAttribute ("PathlossModel", StringValue ("ns3::HybridBuildingsPropagationLossModel"));
//	  lteHelper->SetPathlossModelAttribute ("ShadowSigmaExtWalls", DoubleValue (0));
//	  lteHelper->SetPathlossModelAttribute ("ShadowSigmaOutdoor", DoubleValue (1));
//	  lteHelper->SetPathlossModelAttribute ("ShadowSigmaIndoor", DoubleValue (1.5));
//	  lteHelper->SetPathlossModelAttribute ("Los2NlosThr", DoubleValue (1e6));
	  lteHelper->SetSpectrumChannelType ("ns3::MultiModelSpectrumChannel");

	if (epc)
	{
		epcHelper = CreateObject<PointToPointEpcHelper> ();
		lteHelper->SetEpcHelper (epcHelper);
	}

	mobility.Install (macroEnbs);
	BuildingsHelper::Install (macroEnbs);
	Ptr<LteHexGridEnbTopologyHelper> lteHexGridEnbTopologyHelper = CreateObject<LteHexGridEnbTopologyHelper> ();
	lteHexGridEnbTopologyHelper->SetLteHelper (lteHelper);
	lteHexGridEnbTopologyHelper->SetAttribute ("InterSiteDistance", DoubleValue (interSiteDistance));
	lteHexGridEnbTopologyHelper->SetAttribute ("MinX", DoubleValue (interSiteDistance/2));
	lteHexGridEnbTopologyHelper->SetAttribute ("GridWidth", UintegerValue (nEnbsX));
	Config::SetDefault ("ns3::LteEnbPhy::TxPower", DoubleValue (enbsTx));
	lteHelper->SetEnbAntennaModelType ("ns3::ParabolicAntennaModel");
	lteHelper->SetEnbAntennaModelAttribute ("Beamwidth",   DoubleValue (70));
	lteHelper->SetEnbAntennaModelAttribute ("MaxAttenuation",     DoubleValue (20.0));
	lteHelper->SetEnbDeviceAttribute ("DlEarfcn", UintegerValue (enbEARFCN));
	lteHelper->SetEnbDeviceAttribute ("UlEarfcn", UintegerValue (enbEARFCN + 18000));
	lteHelper->SetEnbDeviceAttribute ("DlBandwidth", UintegerValue (enbBandwidth));
	lteHelper->SetEnbDeviceAttribute ("UlBandwidth", UintegerValue (enbBandwidth));
	NetDeviceContainer macroEnbDevs = lteHexGridEnbTopologyHelper->SetPositionAndInstallEnbDevice (macroEnbs);

	if (epc)
	{
		lteHelper->AddX2Interface (macroEnbs);
	}

	///////////////////////////////////////////////////////////////////////////
	//	ALLOW UE MEASUREMENTS
	///////////////////////////////////////////////////////////////////////////

	LteRrcSap::ReportConfigEutra config;
	config.eventId = LteRrcSap::ReportConfigEutra::EVENT_A2;
	config.threshold1.choice = LteRrcSap::ThresholdEutra::THRESHOLD_RSRQ;
	config.threshold1.range = 26;
	config.triggerQuantity = LteRrcSap::ReportConfigEutra::RSRQ;
	config.reportInterval = LteRrcSap::ReportConfigEutra::MS240;
	config.timeToTrigger = 240;

	std::vector<uint8_t> measIdList;

	NetDeviceContainer::Iterator it;
	for (it = macroEnbDevs.Begin (); it != macroEnbDevs.End (); it++)
	{
	  Ptr<NetDevice> dev = *it;
	  Ptr<LteEnbNetDevice> enbDev = dev->GetObject<LteEnbNetDevice> ();
	  Ptr<LteEnbRrc> enbRrc = enbDev->GetRrc ();

	  uint8_t measId = enbRrc->AddUeMeasReportConfig (config);
	  measIdList.push_back (measId);
	}
}

void
DemoHelper::CreateUsers(NodeContainer& macroUes, MobilityHelper& mobility, Box& macroUeBox, Ptr <LteHelper> lteHelper, uint32_t nUes, double uesSpeed)
{
	macroUes.Create (nUes);

	Ptr<PositionAllocator> positionAlloc = CreateObject<RandomBoxPositionAllocator> ();
	mobility.SetPositionAllocator (positionAlloc);
	lteHelper->SetUeDeviceAttribute ("CsgId", UintegerValue (1));

	if (uesSpeed!=0.0)
	{
		mobility.SetMobilityModel ("ns3::SteadyStateRandomWaypointMobilityModel");
	    Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::MinX", DoubleValue (macroUeBox.xMin));
	    Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::MinY", DoubleValue (macroUeBox.yMin));
	    Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::MaxX", DoubleValue (macroUeBox.xMax));
	    Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::MaxY", DoubleValue (macroUeBox.yMax));
	    Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::Z", DoubleValue (1.5));
		Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::MaxSpeed", DoubleValue (uesSpeed));
		Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::MinSpeed", DoubleValue (uesSpeed));

		positionAlloc = CreateObject<RandomBoxPositionAllocator> ();
		mobility.SetPositionAllocator (positionAlloc);
		mobility.Install (macroUes);

		for (NodeContainer::Iterator it = macroUes.Begin (); it != macroUes.End (); ++it)
		{
			(*it)->Initialize ();
		}
	}
	else
	{
		positionAlloc = CreateObject<RandomBoxPositionAllocator> ();
		Ptr<UniformRandomVariable> xVal = CreateObject<UniformRandomVariable> ();
		xVal->SetAttribute ("Min", DoubleValue (macroUeBox.xMin));
		xVal->SetAttribute ("Max", DoubleValue (macroUeBox.xMax));
		positionAlloc->SetAttribute ("X", PointerValue (xVal));
		Ptr<UniformRandomVariable> yVal = CreateObject<UniformRandomVariable> ();
		yVal->SetAttribute ("Min", DoubleValue (macroUeBox.yMin));
		yVal->SetAttribute ("Max", DoubleValue (macroUeBox.yMax));
		positionAlloc->SetAttribute ("Y", PointerValue (yVal));
		Ptr<UniformRandomVariable> zVal = CreateObject<UniformRandomVariable> ();
		zVal->SetAttribute ("Min", DoubleValue (macroUeBox.zMin));
		zVal->SetAttribute ("Max", DoubleValue (macroUeBox.zMax));
		positionAlloc->SetAttribute ("Z", PointerValue (zVal));
		mobility.SetPositionAllocator (positionAlloc);
		mobility.Install (macroUes);
	}
	BuildingsHelper::Install (macroUes);
}

void
DemoHelper::CreateEPC(Ptr<PointToPointEpcHelper>& epcHelper, Ptr <LteHelper> lteHelper, NodeContainer& macroUes, bool useUdp, bool epcDl, bool epcUl, uint16_t nBearersPerUe)
{
	NetDeviceContainer macroUeDevs = lteHelper->InstallUeDevice (macroUes);

	Ipv4Address remoteHostAddr;
	NodeContainer ues;
	Ipv4StaticRoutingHelper ipv4RoutingHelper;
	Ipv4InterfaceContainer ueIpIfaces;
	Ptr<Node> remoteHost;
	NetDeviceContainer ueDevs;

	// Create a single RemoteHost
	NodeContainer remoteHostContainer;
	remoteHostContainer.Create (1);
	remoteHost = remoteHostContainer.Get (0);
	InternetStackHelper internet;
	internet.Install (remoteHostContainer);

	// Create the Internet
	PointToPointHelper p2ph;
	p2ph.SetDeviceAttribute ("DataRate", DataRateValue (DataRate ("100Gb/s")));
	p2ph.SetDeviceAttribute ("Mtu", UintegerValue (1500));
	p2ph.SetChannelAttribute ("Delay", TimeValue (Seconds (0.010)));
	Ptr<Node> pgw = epcHelper->GetPgwNode ();
	NetDeviceContainer internetDevices = p2ph.Install (pgw, remoteHost);
	Ipv4AddressHelper ipv4h;
	ipv4h.SetBase ("1.0.0.0", "255.0.0.0");
	Ipv4InterfaceContainer internetIpIfaces = ipv4h.Assign (internetDevices);
	// in this container, interface 0 is the pgw, 1 is the remoteHost
	remoteHostAddr = internetIpIfaces.GetAddress (1);

	Ptr<Ipv4StaticRouting> remoteHostStaticRouting = ipv4RoutingHelper.GetStaticRouting (remoteHost->GetObject<Ipv4> ());
	remoteHostStaticRouting->AddNetworkRouteTo (Ipv4Address ("7.0.0.0"), Ipv4Mask ("255.0.0.0"), 1);

	// for internetworking purposes, consider together home UEs and macro UEs
	ues.Add (macroUes);
	ueDevs.Add (macroUeDevs);

	// Install the IP stack on the UEs
	internet.Install (ues);
	ueIpIfaces = epcHelper->AssignUeIpv4Address (NetDeviceContainer (ueDevs));

	// attachment (needs to be done after IP stack configuration)
	// using initial cell selection
	lteHelper->Attach (macroUeDevs);


	// Install and start applications on UEs and remote host
	uint16_t dlPort = 10000;
	uint16_t ulPort = 20000;

	// randomize a bit start times to avoid simulation artifacts
	// (e.g., buffer overflows due to packet transmissions happening
	// exactly at the same time)
	Ptr<UniformRandomVariable> startTimeSeconds = CreateObject<UniformRandomVariable> ();
	if (useUdp)
	  {
		startTimeSeconds->SetAttribute ("Min", DoubleValue (0));
		startTimeSeconds->SetAttribute ("Max", DoubleValue (0.010));
	  }
	else
	  {
		// TCP needs to be started late enough so that all UEs are connected
		// otherwise TCP SYN packets will get lost
		startTimeSeconds->SetAttribute ("Min", DoubleValue (0.100));
		startTimeSeconds->SetAttribute ("Max", DoubleValue (0.110));
	  }

	for (uint32_t u = 0; u < ues.GetN (); ++u)
		  {
			Ptr<Node> ue = ues.Get (u);
			// Set the default gateway for the UE
			Ptr<Ipv4StaticRouting> ueStaticRouting = ipv4RoutingHelper.GetStaticRouting (ue->GetObject<Ipv4> ());
			ueStaticRouting->SetDefaultRoute (epcHelper->GetUeDefaultGatewayAddress (), 1);

			for (uint32_t b = 0; b < nBearersPerUe; ++b)
			  {
				++dlPort;
				++ulPort;

				ApplicationContainer clientApps;
				ApplicationContainer serverApps;

				if (useUdp)
				  {
					if (epcDl)
					  {
						UdpClientHelper dlClientHelper (ueIpIfaces.GetAddress (u), dlPort);
						clientApps.Add (dlClientHelper.Install (remoteHost));
						PacketSinkHelper dlPacketSinkHelper ("ns3::UdpSocketFactory",
															 InetSocketAddress (Ipv4Address::GetAny (), dlPort));
						serverApps.Add (dlPacketSinkHelper.Install (ue));
					  }
					if (epcUl)
					  {
						UdpClientHelper ulClientHelper (remoteHostAddr, ulPort);
						clientApps.Add (ulClientHelper.Install (ue));
						PacketSinkHelper ulPacketSinkHelper ("ns3::UdpSocketFactory",
															 InetSocketAddress (Ipv4Address::GetAny (), ulPort));
						serverApps.Add (ulPacketSinkHelper.Install (remoteHost));
					  }
				  }
				else // use TCP
				  {
					if (epcDl)
					  {
						BulkSendHelper dlClientHelper ("ns3::TcpSocketFactory",
													   InetSocketAddress (ueIpIfaces.GetAddress (u), dlPort));
						dlClientHelper.SetAttribute ("MaxBytes", UintegerValue (0));
						clientApps.Add (dlClientHelper.Install (remoteHost));
						PacketSinkHelper dlPacketSinkHelper ("ns3::TcpSocketFactory",
															 InetSocketAddress (Ipv4Address::GetAny (), dlPort));
						serverApps.Add (dlPacketSinkHelper.Install (ue));
					  }
					if (epcUl)
					  {
						BulkSendHelper ulClientHelper ("ns3::TcpSocketFactory",
													   InetSocketAddress (remoteHostAddr, ulPort));
						ulClientHelper.SetAttribute ("MaxBytes", UintegerValue (0));
						clientApps.Add (ulClientHelper.Install (ue));
						PacketSinkHelper ulPacketSinkHelper ("ns3::TcpSocketFactory",
															 InetSocketAddress (Ipv4Address::GetAny (), ulPort));
						serverApps.Add (ulPacketSinkHelper.Install (remoteHost));
					  }
				  } // end if (useUdp)

				Ptr<EpcTft> tft = Create<EpcTft> ();
				if (epcDl)
				  {
					EpcTft::PacketFilter dlpf;
					dlpf.localPortStart = dlPort;
					dlpf.localPortEnd = dlPort;
					tft->Add (dlpf);
				  }
				if (epcUl)
				  {
					EpcTft::PacketFilter ulpf;
					ulpf.remotePortStart = ulPort;
					ulpf.remotePortEnd = ulPort;
					tft->Add (ulpf);
				  }

				if (epcDl || epcUl)
				  {
					EpsBearer bearer (EpsBearer::NGBR_VIDEO_TCP_DEFAULT);
					lteHelper->ActivateDedicatedEpsBearer (ueDevs.Get (u), bearer, tft);
				  }
				Time startTime = Seconds (startTimeSeconds->GetValue ());
				serverApps.Start (startTime);
				clientApps.Start (startTime);

			  } // end for b
		  }
}

void
DemoHelper::NoEPC()
{

}

