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
#include <signal.h>
#include <unistd.h>
#include <thread>
#include <algorithm>

ConfigureInOut confInOut;

using namespace ns3;

const int NUMBER_OF_UES = 105;	// number of users
int remStep = 0;		// Step number for REM generating
//int lastStepRem = -1;	// For preventing to create same REM multiple times in a row
volatile sig_atomic_t flag = 0;
bool remReady = true;
bool createRem = false;
ConfigurationLog confPrevious;
std::thread threadRem;

// FOR LABELING:
bool labeling = false;
bool labelingStarted = false;
bool labelings[200] = { false };

//float max[2];
//float min[2];
//Vector3D userLocations[NUMBER_OF_UES]; // TODO: MAKE THIS!

struct Triangle
{
	Location A = {0,0};
	Location B = {0,0};
	Location C = {0,0};
};

Triangle triangle;
float triangleA = std::numeric_limits<float>::min();
float triangleB = std::numeric_limits<float>::min();
float triangleC = std::numeric_limits<float>::max();

/*  ////////////////////////////////
 * 	//  LABELING
 *  ////////////////////////////////
 *
 * 	Five first rounds -> Check handovers and calculate rectangle based on handovers
 *	TODO: Check correctness of rectangle.
 *
 *	After rectangle created, create outage
 *	Check anyone moving that area -> mark labels
 */


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//	MACHINE LEARNING
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

float TriangleArea(Triangle t)
{
	 return 0.5 *(-t.B.y*t.C.x + t.A.y*(-t.B.x + t.C.x) + t.A.x*(t.B.y - t.C.y) + t.B.x*t.C.y);
}
float sign (Triangle t)
{
    return (t.A.x - t.C.x) * (t.B.y - t.C.y) - (t.B.x - t.C.x) * (t.A.y - t.C.y);
}

bool
IsPointInsideTriangle(Triangle t, Location p)
{
	float s1 = 1/(2*TriangleArea(t))*(t.A.y*t.C.x - t.A.x*t.C.y + (t.C.y - t.A.y)*p.x + (t.A.x - t.C.x)*p.y);
	float t1 = 1/(2*TriangleArea(t))*(t.A.x*t.B.y - t.A.y*t.B.x + (t.A.y - t.B.y)*p.x + (t.B.x - t.A.x)*p.y);

	if(s1 < 0) return false;
	if(t1 < 0) return false;
	if((1 - s1 - t1) < 0) return false;
	return true;
}

void
CreateTriangle()
{
	std::vector<uint16_t> cells;
	cells.push_back(10);
	cells.push_back(11);
	cells.push_back(12);
	std::vector<Location> locations = confInOut.ReadHandovers(cells);

	for(unsigned int i = 0; i < locations.size(); i++)
	{
		// TRIANGLE
		if(locations[i].x > triangleA)
		{
			triangleA = locations[i].x;
			triangle.A = locations[i];
		}
		if(locations[i].y > triangleB)
		{
			triangleB = locations[i].y;
			triangle.B = locations[i];
		}
		if(locations[i].y < triangleC)
		{
			triangleC = locations[i].y;
			triangle.C = locations[i];
		}
	}
	std::cout << "Triangle is { A: " << triangle.A.x << " : " << triangle.A.y << " B: " << triangle.B.x << " : " << triangle.B.y << " C: " << triangle.C.x << " : " << triangle.C.y << " } " << "\n";
}


std::vector<u_int16_t> outaged;

void
SignalHandler(int signum)
{

	if(signum == SIGUSR1)
	{
		remReady = true;
	}
	else
	{
		flag = 0;
	}
//	else if(signum == SIGINT)
//	{
//		pid_t pid = fork();
//		if(pid == 0)
//		{
//
//		}
//		else
//		{
//			kill(pid, SIGINT);
//		}
//		flag = 0;
//		signal(SIGINT, SIG_DFL);
//		kill(::getpid(), SIGINT);
//		raise(SIGINT);
//		exit(0);
//	}
}

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


/*
 *  Changes cells transmission power
 */
double
GetCellTransmissionPower(u_int16_t cellId)
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

				// get attribute directly:
				return phy->GetTxPower();
			}
		}
	}
	return -1.0;
}


/*
 *  Changes cells transmission power
 */
void
GetTransmissionPowerOfAllCells(double txs[])
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
			if(enbDevice)
			{
				Ptr<LteEnbPhy> phy = enbDevice->GetPhy();

				// get attribute directly:
				txs[enbDevice->GetCellId()] = (phy->GetTxPower());
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
	Vector3D location = GetUeLocation(imsi);
	confInOut.LogHandover(Simulator::Now().GetSeconds(), (int)location.x, (int)location.y, imsi, HandoverEndOK, cellId, 0);
}


void
HandoverStartCallback(std::string context, uint64_t imsi, uint16_t cellid, uint16_t rnti, uint16_t targetCellId)
{
	Vector3D location = GetUeLocation(imsi);
	confInOut.LogHandover(Simulator::Now().GetSeconds(), location.x, location.y, imsi, HandoverStart, cellid, targetCellId);
}

void
A2RsrqEnterCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrq)
{
	Vector3D location = GetUeLocation(imsi);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, A2RSRQEnter, cellId, rsrq);
}

void
A2RsrpEnterCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrq)
{
	Vector3D location = GetUeLocation(imsi);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, A2RSRPEnter, cellId, rsrq);
}

void
A2RsrpLeaveCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsr)
{
	Vector3D location = GetUeLocation(imsi);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, A2RSRPLeave, cellId, rsr);
}

void
A2RsrqLeaveCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsr)
{
	Vector3D location = GetUeLocation(imsi);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, A2RSRQLeave, cellId, rsr);
}

void
A3RsrpEnterCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrp)
{
	Vector3D location = GetUeLocation(imsi);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, A3RSRPEnter, cellId, rsrp);
}

void
OutOfSynchCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrp, double thresh)
{
	Vector3D location = GetUeLocation(imsi);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, OutOfSynch, cellId, rsrp);
}

void
RadioLinkFailureCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrp)
{
	Vector3D location = GetUeLocation(imsi);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, RLF, cellId, rsrp);
}

void
KpiTestCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrp, double rsrq, uint16_t connected)
{
	Vector3D location = GetUeLocation(imsi);
	bool conn = false;
	if(connected == cellId)
	{
		conn = true;
	}
	if(labeling)
	{
		bool label = false;
		if(labelingStarted)
		{
			if(IsPointInsideTriangle(triangle, Location(location.x, location.y)))
			{
				label = true;
			}
		}
//		if(labelings[imsi]) label = true;
//		else
//		{
//			if(std::find(outaged.begin(), outaged.end(), connected) != outaged.end())
//			{
//				label = true;
//				labelings[imsi] = true;
//			}
//		}
		confInOut.LogMainKpisWithLabeling(Simulator::Now().GetSeconds(), location.x, location.y, imsi, cellId, rsrp, rsrq, conn, label);
	}
	else confInOut.LogMainKpis(Simulator::Now().GetSeconds(), location.x, location.y, imsi, cellId, rsrp, rsrq, conn);

}

// For getting rid of double calls // TODO: reason for double calls?
uint64_t lastImsi = 0;

void
ReportUeSinr(double time, uint64_t imsi, uint16_t cellId, double sinr)
{
	if(imsi != lastImsi)
		confInOut.LogSinr(time, imsi, cellId, sinr); // Converted into dBs in PhyStatsCalculator class.
	lastImsi = imsi;
}

void
ReportEnbSinr(double time, uint64_t imsi, uint16_t cellId, double sinr)
{
//	if(imsi != lastImsi)
//		confInOut.LogSinr(time, imsi, cellId, sinr); // Converted into dBs in PhyStatsCalculator class.
//	lastImsi = imsi;
}

void
RemCallback(double x, double y, double z, double sinr)
{
	confInOut.LogREM(x, y, z, sinr);
}


void
WriteUeThroughPut(Ptr<RadioBearerStatsCalculator> rlcStats)
{
	for(int i = 1; i <= NUMBER_OF_UES; ++i)
	{
		double rxBytes = rlcStats->GetDlRxData(i , 4) * 8.0; // bits
		confInOut.LogThroughput(Simulator::Now().GetSeconds(), uint64_t(i), GetConnectedCell(i), rxBytes);
	}
	Simulator::Schedule(MilliSeconds (200), &WriteUeThroughPut, rlcStats);
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// END:		CALLBACKS
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void
GenerateRemMap(Ptr<RadioEnvironmentMapHelper> remHelper, Box macroUeBox)
{
	remHelper->SetAttribute ("ChannelPath", StringValue ("/ChannelList/0"));
	remHelper->SetAttribute ("OutputFile", StringValue ("CSONREM.rem"));
	remHelper->SetAttribute ("XMin", DoubleValue (macroUeBox.xMin));
	remHelper->SetAttribute ("XMax", DoubleValue (macroUeBox.xMax));
	remHelper->SetAttribute ("YMin", DoubleValue (macroUeBox.yMin));
	remHelper->SetAttribute ("YMax", DoubleValue (macroUeBox.yMax));
	remHelper->SetAttribute ("Z", DoubleValue (1.5));
    remHelper->Install();
}



/* Apply changes from updated configuration */
void
ApplyChanges(ConfigurationLog confData)
{
	for(uint i = 0; i < confData.configurations.size(); ++i)
	{
		SetCellTransmissionPower(confData.configurations[i].cellId, confData.configurations[i].txPower);
	}
}

void
ApplySONEngineMethods(SONEngineLog confData)
{
	for(uint i = 0; i < confData.configurations.size(); ++i)
	{
		std::cout << "Clicked: \"" << SONEngineLog::GetMethodName(confData.configurations[i].method) <<
				"\" for cell " << confData.configurations[i].cellId << std::endl;
		double oldTxPower = GetCellTransmissionPower(confData.configurations[i].cellId);


		if(confData.configurations[i].method == SONEngineConfiguration::SonEngineMethod::Outage)
		{
			SetCellTransmissionPower(confData.configurations[i].cellId, 0.0);
			std::cout << "Outage created at cell " << confData.configurations[i].cellId << ": decreased transmission power from "
					  << oldTxPower << " to " << 0.0 << std::endl;

			confInOut.UpdateTxPower(confData.configurations[i].cellId, 0.0);
		}
//		else if(confData.configurations[i].method == SONEngineConfiguration::SonEngineMethod::Normal)
//		{
//			SetCellTransmissionPower(confData.configurations[i].cellId, 46.0);
//						std::cout << "OPERATIONS TAKEN: lowered cells " << confData.configurations[i].cellId << " transmission power from "
//								  << oldTxPower << " to " << 46.0 << std::endl;
//		}

//		if(oldTxPower >= 0)
//		{
//			double newTxPower = oldTxPower - 1.0;
//			if(newTxPower < 0) newTxPower = 0.0;
//			SetCellTransmissionPower(confData.configurations[i].cellId, newTxPower);
//
//			std::cout << "OPERATIONS TAKEN: lowered cells " << confData.configurations[i].cellId << " transmission power from "
//				<< oldTxPower << " to " << newTxPower << std::endl;
//		}
//		else
//		{
//			std::cout << "ERROR: cell number " << confData.configurations[i].cellId << " doesn't exist " << std::endl;
//		}
	}
}

/* Saves cell states to database TODO: maybe would only be called when setup is changed */
void
UpdateCellStates(int noCells)
{
	double txPowerOfAllCells[noCells +1];
	GetTransmissionPowerOfAllCells(txPowerOfAllCells);
	confInOut.SaveCellsStates(txPowerOfAllCells, noCells, remStep);
	remStep++;
}

bool
CheckIfSameConfigurations(ConfigurationLog conf1, ConfigurationLog conf2)
{
	if(conf1.configurations.size() != conf2.configurations.size()) return false;

	for(unsigned int i = 0; i < conf1.configurations.size(); i++)
	{
		if(conf1.configurations[i].txPower != conf2.configurations[i].txPower
				&& conf1.configurations[i].cellId == conf2.configurations[i].cellId) return false;
	}
	return true;
}

/* Reads changes from configuration file and apply changes if updated */
void Update(int nMacroEnbSites)
{
	SONEngineLog confSON = confInOut.ReadSONEngineMethodsFromDatabase();
	ApplySONEngineMethods(confSON);
	ConfigurationLog conf = confInOut.ReadConfigurationFromDatabase();
	// Check if same
	if(CheckIfSameConfigurations(confPrevious, conf))
	{
		createRem = false;
	}
	else
	{
		confPrevious.Clone(conf);
		ApplyChanges(conf);
		createRem = true;
	}
	UpdateCellStates(nMacroEnbSites*3);
}

/* Maybe not needed: should be part of update routine reading from db */
void
WaitSonEngine()
{
	// todo: wait SON engine to make new configuration..
	// currently waiting 1 seconds:
	//usleep(1000000);
}

/* Creates outage in cells 10, 11, 12 */
void
CellOutage()
{
	outaged.push_back(10);
	outaged.push_back(11);
	outaged.push_back(12);
	SetCellTransmissionPower(10, 0.0);
	SetCellTransmissionPower(11, 0.0);
	SetCellTransmissionPower(12, 0.0);
}

/* Saves simulation setup. This will be done once, at the start of the simulation */
void
SaveSimulationState(int nMacroEnbSites, int nMacroEnbSitesX, double interSiteDistance)
{
	// Do we need to save number of UES?
	int pid = ::getpid();
	confInOut.SaveSimulationState(nMacroEnbSites, nMacroEnbSitesX, interSiteDistance, pid);
	UpdateCellStates(nMacroEnbSites*3);
}

void
RunSimulation(double seconds, Ptr<RadioBearerStatsCalculator> rlcStats)
{
    Simulator::Stop (Seconds (seconds));
	Simulator::Run ();
	rlcStats->SetAttribute ("EpochDuration", TimeValue (Seconds (rlcStats->GetEpoch().GetSeconds() + seconds)));
}

void
RunREMGeneratorScript()
{
	// prevent for creating same REM multiple times a row
//	if(lastStepRem != remStep)
//	{
//		std::cout << "LAST STEP: " << lastStepRem << "   STEP: " << remStep << std::endl;
//		lastStepRem = remStep;
		confInOut.RunREMGeneratorScript(remStep);
//	}
}

void
RunREMGenerator()
{
	if(threadRem.joinable())
	{
		threadRem.join();
	}
	remReady = false;
	threadRem = std::thread(RunREMGeneratorScript);
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
                                          ns3::UintegerValue (7),
                                          ns3::MakeUintegerChecker<uint32_t> ());
static ns3::GlobalValue g_nMacroEnbSitesX ("nMacroEnbSitesX",
                                           "(minimum) number of sites along the X-axis of the hex grid",
                                           ns3::UintegerValue (2),
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
static ns3::GlobalValue g_labeling ("labeling",
                               	   "If true, simulation will be running 10 rounds, 5 rounds with normal,"
                               	   "and 5 rounds after outage. Users affected by outage will be label"
                               	   "with LABEL : true.",
								   ns3::BooleanValue (false),
								   ns3::MakeBooleanChecker ());


// TODO: Should add more global values!

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
	GlobalValue::GetValueByName ("labeling", booleanValue);
	labeling = booleanValue.Get ();
	double txPower = 40.0;

	Ptr <LteHelper> lteHelper = CreateObject<LteHelper> ();
	lteHelper->SetHandoverAlgorithmType("ns3::A3RsrpHandoverAlgorithm");
	Ptr<PointToPointEpcHelper> epcHelper;
	MobilityHelper mobility;
	Box macroUeBox;
	NetDeviceContainer macroUeDevs;
	NodeContainer macroUes;


	///////////////////////////////////////////////
	// CREATE TOPOLOGY
	///////////////////////////////////////////////

	DemoHelper::CreateHexagonalTopology(epcHelper, mobility, macroUeBox, lteHelper, nMacroEnbSites, nMacroEnbSitesX, interSiteDistance, epc, txPower, 100, 25);

	///////////////////////////////////////////////
	// CREATE USERS
	///////////////////////////////////////////////

	DemoHelper::CreateUsers(macroUes, mobility, macroUeBox, lteHelper, NUMBER_OF_UES, 16.67);

	///////////////////////////////////////////////
	// CREATE INTERNET
	///////////////////////////////////////////////

	if(epc)
	{
		DemoHelper::CreateEPC(epcHelper, lteHelper, macroUes, false, true, true, 1);
	}
	else
	{
		// Todo: Probably not needed
		DemoHelper::NoEPC();
	}

	///////////////////////////////////////////////
	// CONNECT TO DATABASE
	///////////////////////////////////////////////

	confInOut.CreateConnectionToDataBase();
	confInOut.SetDatabase("5gopt");

	///////////////////////////////////////////////
	// SET CALLBACKS
	///////////////////////////////////////////////

	lteHelper->EnableTraces();

	// Throuhput
	Ptr<RadioBearerStatsCalculator> rlcStats = lteHelper->GetRlcStats ();
	rlcStats->SetAttribute ("StartTime", TimeValue (Seconds (0)));
//	rlcStats->SetAttribute ("EpochDuration", TimeValue (Seconds (99999999999)));
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
	phyStats->TraceConnectWithoutContext("SinrUeTrace", MakeCallback(&ReportUeSinr));
	phyStats->TraceConnectWithoutContext("SinrEnbTrace", MakeCallback(&ReportEnbSinr));

	///////////////////////////////////////////////
	// DEMO LOOP
	///////////////////////////////////////////////

//	// Register signal handler
	signal(SIGUSR1, SignalHandler);
	signal(SIGINT, SIG_DFL);


	// Clear state to database for the REM
	confInOut.ClearSimulationState();
	confInOut.InitializeCellConfigurations(txPower, nMacroEnbSites * 3);

	// Save state to database for the REM
	SaveSimulationState(nMacroEnbSites, nMacroEnbSitesX, interSiteDistance);

	// Generate REM
	RunREMGenerator();


//	// Initialize locations:
//	for(int i = 0; i< NUMBER_OF_USERS; i++)
//	{
//		userLocations[i] = Vector
//	}

	int rounds = 0;
	while(flag == 0 && rounds < 12)
	{
		// read configuration from database:
		Update(nMacroEnbSites); 	// Note! requires connection to database

		// Create REM
		if(remReady && createRem)
		{
			RunREMGenerator();
		}

		// run simulation:
		RunSimulation(simTime, rlcStats);
		// Updates cell states to database:
		UpdateCellStates(nMacroEnbSites*3); // <- IF REM
		// write KPIs into database:
		confInOut.FlushLogs();
		std::cout << "Measurements are written to database.." << std::endl;

		if(labeling)
		{
			rounds++;
			if(rounds <= 6)
			{
				CreateTriangle();
			}
			if(rounds == 6)
			{
				CellOutage();
				labelingStarted = true;
			}
		}
	}
	lteHelper = 0;
	Simulator::Destroy ();

}

/*
 RUN COMMANDS:
 -------------

./waf --run="CSONDemo --simTime=5 --ns3::LteHelper::HandoverAlgorithm=ns3::A3RsrpHandoverAlgorithm"

*/
