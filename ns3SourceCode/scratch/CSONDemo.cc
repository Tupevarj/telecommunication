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
#include <ns3/rng-seed-manager.h>
#include <signal.h>
#include <unistd.h>
#include <thread>
#include <algorithm>
#include <time.h>
#include <iomanip>
#include <string>


#ifdef DEBUG
clock_t timeStart; // = clock();
clock_t timePrevious; // = clock();
#endif //DEBUG


using namespace ns3;

/*--------------------------------------------------------------------------------------------------------------------*/

DatabaseConnector dbConnector;			// Object that handles all the communication with database
const int NUMBER_OF_UES = 105;			// Number of users (CONSTANT)
Vector3D ueLocBuffer[NUMBER_OF_UES+1];	// User locations in buffer (Used to reduce calculations when multiple
										// events logged for same UE in same time)
int remStep = 0;						// Step number for REM generating (NOT NEEDED WHEN USING DB!)
volatile sig_atomic_t flag = 0;			// Flag for exit simulation
bool remReady = true;					// True if generating REM is finished
bool createRem = true;  				// True if REM is needed to generate
bool labeling = false;					// If true, then training simulation is ran
ConfigurationLog confPrevious;  		// Configuration of previous update step
std::thread threadRem;					// Thread for REM generator process

/*--------------------------------------------------------------------------------------------------------------------*/


std::string DoubleToString(double number)
{
	std::stringstream ss;
	ss << std::fixed << std::setprecision(1) << number;
	return ss.str();
}

std::string IntToString(int number)
{
	std::stringstream ss;
	ss << number;
	return ss.str();
}

void
LogStatusCallback(std::string message, int type)
{
	dbConnector.LogStatus(DoubleToString(Simulator::Now().GetSeconds()), message, type);
}

/*
 * Returns cell ids of particular basestation
 */
void
GetCellBasedOnBsID(uint16_t bs, std::vector<uint16_t>& ids)
{
	uint16_t start = (bs - 1) * 3 + 1;
	for(uint16_t i = 0; i < 3; i++)
	{
		ids.push_back(start + i);
	}
}

void
SignalHandler(int signum)
{

	if(signum == SIGUSR1)
	{
		remReady = true;
	}
	else if(signum == SIGUSR2)
	{
		LogStatusCallback("Simulation ended", 3);
		dbConnector.FlushLogs();
		raise(SIGKILL);
	}
	else if(signum == SIGIOT)
	{
		LogStatusCallback("ERROR: Simulation ended", 0);
		dbConnector.FlushLogs();
		signal(SIGIOT, SIG_DFL);
		raise(SIGIOT);
	}
	else
	{
		flag = 0;
	}
}


void
UpdateUserLocations(float time)
{
	ueLocBuffer[0] = Vector3D(time,time, time);
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
			if(ueDevice && ueDevice->GetImsi() > 0 && ueDevice->GetImsi() <= NUMBER_OF_UES)
			{
				//Vector3D location = node->GetObject<MobilityModel>()->GetPosition();
				ueLocBuffer[ueDevice->GetImsi()] = node->GetObject<MobilityModel>()->GetPosition();
			}
		}
	}
}

inline bool DoubleEquals(double a, double b, double epsilon = 0.01)
{
    return std::abs(a - b) < epsilon;
}

/*
 * Returns cell locations in array.
 */
std::vector<std::vector<int>>
GetCellLocations(int cellCount, int intersiteDistance)
{
	std::vector<std::vector<int>> locations(cellCount+1);
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
				Ptr<MobilityModel> mob = node->GetObject<MobilityModel>();
				uint16_t cellId = enbDevice->GetCellId();
				Vector3D position = mob->GetPosition();

				// Need to correct cell locations (DEPENDS CELL INTERSITE DISTANCE):
				int remainder = cellId % 3;
				if(remainder == 0) {
					// --
					position.x -= intersiteDistance / 6.25;
					position.y -= intersiteDistance / 4.0;
				}
				else if(remainder == 1) {
					// x+1
					position.x += intersiteDistance / 3.5;
				}
				else if(remainder == 2) {
					// y+1
					position.y += intersiteDistance / 4.0;
					position.x -= intersiteDistance / 6.25;
				}
				locations[cellId] = { (int)position.x , (int)position.y};
			}
		}
	}
	return locations;
}

Vector3D
GetUeLocation(uint64_t imsi)
{
	// For arbitrary timestamps find UE location without buffer
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
 *  Changes basestations transmission power
 */
void
SetBaseStationTransmissionPower(u_int16_t bs, double power)
{
	std::vector<uint16_t> cellIds;
	GetCellBasedOnBsID(bs, cellIds);
	SetCellTransmissionPower(cellIds[0], power);
	SetCellTransmissionPower(cellIds[1], power);
	SetCellTransmissionPower(cellIds[2], power);
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
	dbConnector.LogHandover(Simulator::Now().GetSeconds(), (int)location.x, (int)location.y, imsi, HandoverEndOK, cellId, 0);
}


void
HandoverStartCallback(std::string context, uint64_t imsi, uint16_t cellid, uint16_t rnti, uint16_t targetCellId)
{
	Vector3D location = GetUeLocation(imsi);
	dbConnector.LogHandover(Simulator::Now().GetSeconds(), location.x, location.y, imsi, HandoverStart, cellid, targetCellId);
}

void
A2RsrqEnterCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrq)
{
	Vector3D location = GetUeLocation(imsi);
	dbConnector.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, A2RSRQEnter, cellId, rsrq);
}

void
A2RsrpEnterCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrq)
{
	Vector3D location = GetUeLocation(imsi);
	dbConnector.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, A2RSRPEnter, cellId, rsrq);
}

void
A2RsrpLeaveCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsr)
{
	Vector3D location = GetUeLocation(imsi);
	dbConnector.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, A2RSRPLeave, cellId, rsr);
}

void
A2RsrqLeaveCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsr)
{
	Vector3D location = GetUeLocation(imsi);
	dbConnector.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, A2RSRQLeave, cellId, rsr);
}

void
A3RsrpEnterCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrp)
{
	Vector3D location = GetUeLocation(imsi);
	dbConnector.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, A3RSRPEnter, cellId, rsrp);
}

void
OutOfSynchCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrp, double thresh)
{
	Vector3D location = GetUeLocation(imsi);
	dbConnector.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, OutOfSynch, cellId, rsrp);
}

void
RadioLinkFailureCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrp)
{
	Vector3D location = GetUeLocation(imsi);
	dbConnector.LogEvent(Simulator::Now().GetSeconds(), location.x, location.y, imsi, RLF, cellId, rsrp);
}

std::vector<int> lastRLFs;

/* Check labeling and log main kpis */
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

		// Update RLFs
		if((int)imsi == 1 && cellId == 1)
		{
			lastRLFs = dbConnector.ReadRLFs(Simulator::Now().GetSeconds(), 3.0);
		}

		int counter = 0;
		for(unsigned int i = 0; i < lastRLFs.size(); i++)
		{
			if(lastRLFs[i] == (int)imsi)
			{
				counter++;
				if(counter > 1) {
					label = true;
					break;
				}
			}
		}
		dbConnector.LogMainKpisWithLabeling(Simulator::Now().GetSeconds(), location.x, location.y, imsi, cellId, rsrp, rsrq, conn, label);
	}
	else dbConnector.LogMainKpisWithLabeling(Simulator::Now().GetSeconds(), location.x, location.y, imsi, cellId, rsrp, rsrq, conn, false);

}

// For getting rid of double calls // TODO: reason for double calls?
uint64_t lastImsi = 0;

void
ReportUeSinr(double time, uint64_t imsi, uint16_t cellId, double sinr)
{
	if(imsi != lastImsi)
		dbConnector.LogSinr(time, imsi, cellId, sinr); // Converted into dBs in PhyStatsCalculator class.
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
	dbConnector.LogREM(x, y, z, sinr);
}


void
WriteUeThroughPut(Ptr<RadioBearerStatsCalculator> rlcStats)
{
	for(int i = 1; i <= NUMBER_OF_UES; ++i)
	{
		double rxBytes = rlcStats->GetDlRxData(i , 4) * 8.0; // bits
		dbConnector.LogThroughput(Simulator::Now().GetSeconds(), uint64_t(i), GetConnectedCell(i), rxBytes);
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


		if(confData.configurations[i].method == SONEngineConfiguration::SonEngineMethod::Outage)
		{
			// TODO: continue here: 15.3
			std::vector<uint16_t> cellIds;
			GetCellBasedOnBsID(confData.configurations[i].cellId, cellIds);
			//double oldTxPower = GetCellTransmissionPower(cellIds[0]);

			SetBaseStationTransmissionPower(confData.configurations[i].cellId, 0.0);
			LogStatusCallback("Outage created at basestation " + IntToString(confData.configurations[i].cellId), 2);

			dbConnector.UpdateTxPower(cellIds[0], 0.0);
			dbConnector.UpdateTxPower(cellIds[1], 0.0);
			dbConnector.UpdateTxPower(cellIds[2], 0.0);
		}
	}
}

/* Saves cell states to database TODO: maybe would only be called when setup is changed */
void
UpdateCellStates(int noCells)
{
	double txPowerOfAllCells[noCells +1];
	GetTransmissionPowerOfAllCells(txPowerOfAllCells);
	dbConnector.SaveCellsStates(txPowerOfAllCells, noCells);
	remStep++;
}


bool
CheckIfSameConfigurations(ConfigurationLog conf1, ConfigurationLog conf2)
{
	if(conf1.configurations.size() != conf2.configurations.size()) return false;

	for(unsigned int i = 0; i < conf1.configurations.size(); i++)
	{
		for(unsigned int j = 0; j < conf2.configurations.size(); j++)
		{
			if(conf1.configurations[i].cellId == conf2.configurations[j].cellId)
			{
				if(conf1.configurations[i].txPower != conf2.configurations[j].txPower)
				{
					std::cout << "TX Power has changed for cell " << conf1.configurations[i].cellId << std::endl;
					return false;
				}
				break;
			}
		}
	}
	return true;
}

/* Reads changes from configuration file and apply changes if updated */
void Update(int nMacroEnbSites)
{
	SONEngineLog confSON = dbConnector.ReadSONEngineMethodsFromDatabase();
	ApplySONEngineMethods(confSON);
	ConfigurationLog conf = dbConnector.ReadConfigurationFromDatabase();
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
	//createRem = true;
	UpdateCellStates(nMacroEnbSites*3);
}

/* Saves simulation setup. This will be done once, at the start of the simulation */
void
SaveSimulationState(int nMacroEnbSites, int nMacroEnbSitesX, double interSiteDistance)
{
	// Do we need to save number of UES?
	int pid = ::getpid();
	dbConnector.SaveSimulationState(nMacroEnbSites, nMacroEnbSitesX, interSiteDistance, pid);
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
	dbConnector.RunREMGeneratorScript(remStep);
}

void
RunREMGenerator()
{
	if(threadRem.joinable())
	{
		threadRem.join();
	}
	createRem = false;
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
                                          ns3::UintegerValue (7),			// 19 ja 6
                                          ns3::MakeUintegerChecker<uint32_t> ());
static ns3::GlobalValue g_nMacroEnbSitesX ("nMacroEnbSitesX",
                                           "(minimum) number of sites along the X-axis of the hex grid",
                                           ns3::UintegerValue (2),
                                           ns3::MakeUintegerChecker<uint32_t> ());
static ns3::GlobalValue g_interSiteDistance ("interSiteDistance",
                                             "min distance between two nearby macro cell sites",
                                             ns3::DoubleValue (500), // 1732
                                             ns3::MakeDoubleChecker<double> ());
static ns3::GlobalValue g_epc ("epc",
                               "If true, will setup the EPC to simulate an end-to-end topology, "
                               "with real IP applications over PDCP and RLC UM (or RLC AM by changing "
                               "the default value of EpsBearerToRlcMapping e.g. to RLC_AM_ALWAYS). "
                               "If false, only the LTE radio access will be simulated with RLC SM. ",
                               ns3::BooleanValue (true),
                               ns3::MakeBooleanChecker ());
static ns3::GlobalValue g_training ("training",
                               	   "If true, simulation will be running 10 rounds, 5 rounds with normal,"
                               	   "and 5 rounds after outage. Users affected by outage will be label"
                               	   "with LABEL : true.",
								   ns3::BooleanValue (false),
								   ns3::MakeBooleanChecker ());
static ns3::GlobalValue g_training_bs("outage",
									"Basestation ID to been broken in training-phase",
									ns3::UintegerValue (4),
									ns3::MakeUintegerChecker<uint32_t> ());


// TODO: Make read globals from DB instead in here

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
	GlobalValue::GetValueByName ("training", booleanValue);
	labeling = booleanValue.Get ();
	GlobalValue::GetValueByName ("outage", uintegerValue);
	uint16_t outageBs = uintegerValue.Get ();
	double txPower = 43.0;

	Ptr <LteHelper> lteHelper = CreateObject<LteHelper> ();
	lteHelper->SetHandoverAlgorithmType("ns3::A3RsrpHandoverAlgorithm");
	Ptr<PointToPointEpcHelper> epcHelper;
	MobilityHelper mobility;
	Box macroUeBox;
	NetDeviceContainer macroUeDevs;
	NodeContainer macroUes;
	Config::SetDefault ("ns3::LteEnbRrc::SrsPeriodicity", UintegerValue (160));

	//if(!labeling)
	RngSeedManager::SetSeed(11); // TODO: create random working: 11, 2

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

	dbConnector.CreateConnectionToDataBase();
	dbConnector.SetDatabase("5gopt");
	dbConnector.dropDatabase();
	dbConnector.SetDatabase("5gopt");

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
	signal(SIGUSR2, SignalHandler);
	signal(SIGIOT, SignalHandler);
	//signal(SIGINT, SIG_DFL);

	// Clear state to database for the REM
	dbConnector.ClearSimulationState();
	std::vector<std::vector<int>> cellLocations = GetCellLocations(nMacroEnbSites*3, interSiteDistance);
	dbConnector.InitializeCellConfigurations(txPower, nMacroEnbSites * 3, cellLocations);

	// Save state to database for the REM
	SaveSimulationState(nMacroEnbSites, nMacroEnbSitesX, interSiteDistance);

	// Generate REM
	//RunREMGenerator();

	if(labeling)
	{
		std::stringstream stream;
		stream << std::fixed << std::setprecision(2) << simTime * 200;
		std::string timeStamp = stream.str();
		LogStatusCallback("Training phase started. Training will last " + timeStamp + " seconds in simulation time.", 3);
	}
	else
		LogStatusCallback("Simulation started.", 3);

	int rounds = 0;
	while(flag == 0)
	{
		#ifdef DEBUG
		  timeStart = clock();
		  timePrevious = timeStart;
		#endif //DEBUG
		// read configuration from database:
		Update(nMacroEnbSites); 	// Note! requires connection to database

		// run simulation:
		RunSimulation(simTime, rlcStats);

		// write KPIs into database:
		dbConnector.FlushLogs();
		LogStatusCallback("Measurements from simulation are written to database..", 1);
		std::cout << "Measurements are written to database.." << std::endl;

		#ifdef DEBUG
		  clock_t timeEnd = clock();
		  double timeSpent = (double)(timeEnd - timeStart) / CLOCKS_PER_SEC;
		  std::cout << "Round time: " << timeSpent << std::endl;
		#endif //DEBUG

		//rounds++;
		if(labeling)
		{
			if(rounds == 100)
			{
				SetBaseStationTransmissionPower(outageBs, -100.0);
				createRem = true;
			}
			if(rounds == 200)
			{
				LogStatusCallback("Training Phase Ended.", 3);
				std::cout << "Training Phase Ended" << std::endl;
				break;
			}
			rounds++;
		}

		// Create REM
		if(remReady && createRem)
		{
			RunREMGenerator();
		}
	}
	if(threadRem.joinable())
	{
		threadRem.join();
	}
	dbConnector.FlushLogs();
	lteHelper = 0;
	Simulator::Destroy ();
}

/*
 RUN COMMANDS:
 -------------

./waf --run="CSONDemo --simTime=5 --ns3::LteHelper::HandoverAlgorithm=ns3::A3RsrpHandoverAlgorithm"

*/
