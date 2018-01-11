/*
 * CSONDemo.cc
 *
 *  Created on: 12.12.2017
 *      Author: tupevarj
 */

#include <ns3/core-module.h>
#include <ns3/network-module.h>
#include <ns3/mobility-module.h>
#include <ns3/internet-module.h>
#include <ns3/lte-module.h>
#include <ns3/config-store-module.h>
#include <ns3/buildings-module.h>
#include <ns3/point-to-point-helper.h>
#include <ns3/applications-module.h>
#include <ns3/log.h>

ConfigureInOut confInOut;

using namespace ns3;

const int NUMBER_OF_UES = 20;	// todo: HANKKIUDU EROON!!!


Vector3D
GetUeLocation(uint64_t imsi)
{
	// Loop through all the nodes:
	for(NodeList::Iterator it = NodeList::Begin(); it != NodeList::End(); ++it)
	{
		Ptr<Node> node = *it;
		int nDevices = node->GetNDevices();

		// Loop through all devices on node:
		for(int i = 0; i < nDevices; i++)
		{
			Ptr<LteUeNetDevice> ueDevice = node->GetDevice(i)->GetObject<LteUeNetDevice>();

			// test NULL
			if(ueDevice && ueDevice->GetImsi() == imsi)
			{
				Ptr<MobilityModel> mob = node->GetObject<MobilityModel>();
				return mob->GetPosition();
			}
		}
	}
	return Vector3D(0,0,0);
}


/*
 *  Changes cells transmission power
 */
void
SetCellTransmissionPower(u_int16_t cellId, double power)
{
	// Loop through all the nodes:
	for(NodeList::Iterator it = NodeList::Begin(); it != NodeList::End(); ++it)
	{
		Ptr<Node> node = *it;
		int nDevices = node->GetNDevices();

		// Loop through all devices on node:
		for(int i = 0; i < nDevices; i++)
		{
			Ptr<LteEnbNetDevice> enbDevice = node->GetDevice(i)->GetObject<LteEnbNetDevice>();

			// test NULL
			if(enbDevice && enbDevice->GetCellId() == cellId)
			{
				Ptr<LteEnbPhy> phy = enbDevice->GetPhy();

				// set attribute directly:
				// phy->SetTxPower(power);
				// set attribute through attribute system:
				phy->SetAttribute("TxPower", DoubleValue(power));
				return;
			}
		}
	}
}


uint16_t
GetConnectedCell(uint64_t imsi)
{
	// Loop through all the nodes:
	for(NodeList::Iterator it = NodeList::Begin(); it != NodeList::End(); ++it)
	{
		Ptr<Node> node = *it;
		int nDevices = node->GetNDevices();

		// Loop through all devices on node:
		for(int i = 0; i < nDevices; i++)
		{
			Ptr<LteUeNetDevice> ueDevice = node->GetDevice(i)->GetObject<LteUeNetDevice>();

			// test NULL
			if(ueDevice && ueDevice->GetImsi() == imsi)
			{
				return ueDevice->GetRrc()->GetCellId();
			}
		}
	}
	return 0;
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CALLBACKS
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


void
HandoverEndOkCallback(std::string context, uint64_t imsi, uint16_t cellId, uint16_t rnti)
{
	confInOut.LogHandover(Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, HandoverStart, cellId, 0);
}


void
HandoverStartCallback(std::string context, uint64_t imsi, uint16_t cellid, uint16_t rnti, uint16_t targetCellId)
{
	confInOut.LogHandover(Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, HandoverStart, cellid, targetCellId);
}

void
A2RsrqEnterCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrq)
{
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, A2RSRQEnter, cellId, rsrq);
}

void
A2RsrpEnterCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrq)
{
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, A2RSRPEnter, cellId, rsrq);
}

void
A2RsrpLeaveCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsr)
{
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, A2RSRPLeave, cellId, rsr);
}

void
A2RsrqLeaveCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsr)
{
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, A2RSRQLeave, cellId, rsr);
}

void
A3RsrpEnterCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrp)
{
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, A3RSRPEnter, cellId, rsrp);
}

void
OutOfSynchCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrp, double thresh)
{
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, OutOfSynch, cellId, rsrp);
}

void
RadioLinkFailureCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrp)
{
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, RLF, cellId, rsrp);
}

void
KpiTestCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrp, double rsrq)
{
	confInOut.LogMainKpis(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, cellId, rsrp, rsrq);
}

void
ReportUeSinr(double time, uint64_t imsi, uint16_t cellId, double sinr)
{
	confInOut.LogSinr(time, imsi, cellId, sinr); // Converted into dBs in PhyStatsCalculator class.
}

void
WriteUeThroughPut(Ptr<RadioBearerStatsCalculator> rlcStats)
{
	// last measured throughput for Ues.
	static double lastThrs[NUMBER_OF_UES];

	for(int i = 1; i <= NUMBER_OF_UES; ++i)
	{
		double rxBytes = rlcStats->GetUlRxData(i , 4) * 0.001; // kilobytes		TODO: // SELVITÄ VIELÄ Logical Chanel ID   < LCID!
		double timeNow = Simulator::Now().GetSeconds();

		confInOut.LogThroughput(timeNow, uint64_t(i), GetConnectedCell(i), (rxBytes- lastThrs[i-1]) /0.200);

		lastThrs[i-1] =  rxBytes;
	}
	Simulator::Schedule(MilliSeconds (200), &WriteUeThroughPut, rlcStats);
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// END:		CALLBACKS
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



/* Apply changes from updated configuration */
void
ApplyChanges(ConfigurationLog confData)
{
	for(uint i = 0; i < confData.configurations.size(); ++i)
	{
		SetCellTransmissionPower(confData.configurations[i].cellId, confData.configurations[i].txPower);
	}
}

static int fileNumber = 0;

/* Reads changes from configuration file and apply changes if updated */
void Update()
{
	ConfigurationLog conf = confInOut.ReadConfigurationFromDatabase();
	ApplyChanges(conf);

	std::stringstream strs;
	strs << fileNumber;
	std::string postFix = strs.str();

	fileNumber++;
	Simulator::Schedule (MilliSeconds (3000), &Update);
}

#include <unistd.h>

void
WaitSonEngine()
{
	// todo: wait SON engine to make new configuration..
	// currently waiting 10 seconds:
	usleep(10000000);
}

void
CellOutage()
{
	SetCellTransmissionPower(10, 0.0);
	SetCellTransmissionPower(11, 0.0);
	SetCellTransmissionPower(12, 0.0);
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//		GLOBAL VALUES
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

static ns3::GlobalValue g_simTime ("simTime",
                                   "Total duration of the simulation [s]",
                                   ns3::DoubleValue (0.25),
                                   ns3::MakeDoubleChecker<double> ());
static ns3::GlobalValue g_nMacroEnbSites ("nMacroEnbSites",
                                          "How many macro sites there are",
                                          ns3::UintegerValue (3),
                                          ns3::MakeUintegerChecker<uint32_t> ());
static ns3::GlobalValue g_nMacroEnbSitesX ("nMacroEnbSitesX",
                                           "(minimum) number of sites along the X-axis of the hex grid",
                                           ns3::UintegerValue (1),
                                           ns3::MakeUintegerChecker<uint32_t> ());
static ns3::GlobalValue g_interSiteDistance ("interSiteDistance",
                                             "min distance between two nearby macro cell sites",
                                             ns3::DoubleValue (500),
                                             ns3::MakeDoubleChecker<double> ());
static ns3::GlobalValue g_epc ("epc",
                               "If true, will setup the EPC to simulate an end-to-end topology, "
                               "with real IP applications over PDCP and RLC UM (or RLC AM by changing "
                               "the default value of EpsBearerToRlcMapping e.g. to RLC_AM_ALWAYS). "
                               "If false, only the LTE radio access will be simulated with RLC SM. ",
                               ns3::BooleanValue (true),
                               ns3::MakeBooleanChecker ());


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// END:		GLOBAL VALUES
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

int
main (int argc, char *argv[])
{
	CommandLine cmd;
	cmd.Parse (argc, argv);
	ConfigStore inputConfig;
	inputConfig.ConfigureDefaults ();
	// parse again so you can override input file default values via command line
	cmd.Parse (argc, argv);

	DoubleValue doubleValue;
	UintegerValue uintegerValue;
	BooleanValue booleanValue;
	GlobalValue::GetValueByName ("simTime", doubleValue);
	double simTime = doubleValue.Get();
	GlobalValue::GetValueByName ("nMacroEnbSites", uintegerValue);
	uint32_t nMacroEnbSites = uintegerValue.Get ();
	GlobalValue::GetValueByName ("nMacroEnbSitesX", uintegerValue);
	uint32_t nMacroEnbSitesX = uintegerValue.Get ();
	GlobalValue::GetValueByName ("interSiteDistance", doubleValue);
	double interSiteDistance = doubleValue.Get ();
	GlobalValue::GetValueByName ("epc", booleanValue);
	bool epc = booleanValue.Get ();


	Ptr <LteHelper> lteHelper = CreateObject<LteHelper> ();
	Ptr<PointToPointEpcHelper> epcHelper;
	MobilityHelper mobility;
	Box macroUeBox;
	NetDeviceContainer macroUeDevs;
	NodeContainer macroUes;


	///////////////////////////////////////////////
	// CREATE TOPOLOGY
	///////////////////////////////////////////////

	DemoHelper::CreateHexagonalTopology(epcHelper, mobility, macroUeBox, lteHelper, nMacroEnbSites, nMacroEnbSitesX, interSiteDistance, epc, 43.0, 100, 25);

	///////////////////////////////////////////////
	// CREATE USERS
	///////////////////////////////////////////////

	DemoHelper::CreateUsers(macroUes, mobility, macroUeBox, lteHelper, NUMBER_OF_UES, 16.67);

	///////////////////////////////////////////////
	// CREATE INTERNET
	///////////////////////////////////////////////

	if(epc)
	{
		DemoHelper::CreateEPC(epcHelper, lteHelper, macroUes, true, true, true, 1);
	}
	else
	{
		//todo:
		DemoHelper::NoEPC();
	}

	///////////////////////////////////////////////
	// CONNECT TO DATABASE
	///////////////////////////////////////////////

	confInOut.CreateConnectionToDataBase();
	confInOut.SetDatabase("5gopt");
//	confInOut.SetCollection("collectionII");

	///////////////////////////////////////////////
	// SET CALLBACKS
	///////////////////////////////////////////////

	lteHelper->EnablePhyTraces ();
	lteHelper->EnableDlPhyTraces();
	lteHelper->EnableUlPhyTraces();
	lteHelper->EnableMacTraces ();
	lteHelper->EnableRlcTraces ();
	lteHelper->EnablePdcpTraces ();

	// Throuhput
	Ptr<RadioBearerStatsCalculator> rlcStats = lteHelper->GetRlcStats ();
	rlcStats->SetAttribute ("StartTime", TimeValue (Seconds (0)));
	rlcStats->SetAttribute ("EpochDuration", TimeValue (MilliSeconds (200)));
	Simulator::Schedule(MilliSeconds (200), &WriteUeThroughPut, rlcStats);

	// RLF events
	Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/RadioLinkFailure", MakeCallback (&RadioLinkFailureCallback));
	Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/OutOfSynch", MakeCallback (&OutOfSynchCallback));
	// A2 events
	Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/A2RsrqEnter", MakeCallback (&A2RsrqEnterCallback));
	Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/A2RsrqLeave", MakeCallback (&A2RsrqLeaveCallback));
	Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/A2RsrpLeave", MakeCallback (&A2RsrpLeaveCallback));
	Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/A2RsrpEnter", MakeCallback (&A2RsrpEnterCallback));
	// A3 events
	Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/A3Rsrp", MakeCallback (&A3RsrpEnterCallback));
	// Handover events
	Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/HandoverStart", MakeCallback (&HandoverStartCallback));
	Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/HandoverEndOk", MakeCallback (&HandoverEndOkCallback));
	// Main Kpis
	Config::Connect("/NodeList/*/DeviceList/*/LteUeRrc/KpiTest",  MakeCallback(&KpiTestCallback));
	// SINR
	Ptr<PhyStatsCalculator> phyStats = lteHelper->GetPhyStatsCalculator();
	phyStats->TraceConnectWithoutContext("SinrTrace", MakeCallback(&ReportUeSinr));

	///////////////////////////////////////////////
	// DEMO LOOP
	///////////////////////////////////////////////

//    int rounds = 0;
	while(true)
	{
		// read configuration from database:
		//Update(); // HUOM! requires connection to database
		// run simulation:
	    Simulator::Stop (Seconds (simTime));
		Simulator::Run ();
		// write KPIs into database:
		confInOut.FlushLogs();
		// wait for new configuration from SON engine:
		WaitSonEngine();
//		rounds++;
	}
//	confInOut.RunMatlabKpiScript();
	lteHelper = 0;
	Simulator::Destroy ();

}

/*
 RUN COMMANDS:
 -------------

./waf --run="CSONDemo --simTime=5 --ns3::LteHelper::HandoverAlgorithm=ns3::A3RsrpHandoverAlgorithm"

*/
