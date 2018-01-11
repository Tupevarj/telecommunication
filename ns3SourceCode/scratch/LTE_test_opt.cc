
/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2012 Centre Tecnologic de Telecomunicacions de Catalunya (CTTC)
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Author: Nicola Baldo <nbaldo@cttc.es>
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
#include <iomanip>
#include <ios>
#include <vector>
#include <ctime>

#include <string>
#include <iostream>
#include <fstream>
#include <sstream>


// The topology of this simulation program is inspired from
// 3GPP R4-092042, Section 4.2.1 Dual Stripe Model
// note that the term "apartments" used in that document matches with
// the term "room" used in the BuildingsMobilityModel



///////////////////////////////////////////////////////////////////////////
//
//	CHANGES MADE:
//		- CALLBACK TRACES AND DATA OUTPUT 380 - 500
//		- CONFIGURE SETTERS	505 - 545
//		- CONFIGURATION INPUT, UPDATE AND DATA OUTPUT 550 - 610
//
///////////////////////////////////////////////////////////////////////////



using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("LTE_TEST_OPT");

bool AreOverlapping (Box a, Box b)
{
  return !((a.xMin > b.xMax) || (b.xMin > a.xMax) || (a.yMin > b.yMax) || (b.yMin > a.yMax));
}

void
PrintGnuplottableBuildingListToFile (std::string filename)
{
  std::ofstream outFile;
  outFile.open (filename.c_str (), std::ios_base::out | std::ios_base::trunc);
  if (!outFile.is_open ())
    {
      NS_LOG_ERROR ("Can't open file " << filename);
      return;
    }
  uint32_t index = 0;
  for (BuildingList::Iterator it = BuildingList::Begin (); it != BuildingList::End (); ++it)
    {
      ++index;
      Box box = (*it)->GetBoundaries ();
      outFile << "set object " << index
              << " rect from " << box.xMin  << "," << box.yMin
              << " to "   << box.xMax  << "," << box.yMax
              << " front fs empty "
              << std::endl;
    }
}

void
PrintGnuplottableUeListToFile (std::string filename)
{
  std::ofstream outFile;
  outFile.open (filename.c_str (), std::ios_base::out | std::ios_base::trunc);
  if (!outFile.is_open ())
    {
      NS_LOG_ERROR ("Can't open file " << filename);
      return;
    }
  for (NodeList::Iterator it = NodeList::Begin (); it != NodeList::End (); ++it)
    {
      Ptr<Node> node = *it;
      int nDevs = node->GetNDevices ();
      for (int j = 0; j < nDevs; j++)
        {
          Ptr<LteUeNetDevice> uedev = node->GetDevice (j)->GetObject <LteUeNetDevice> ();
          if (uedev)
            {
              Vector pos = node->GetObject<MobilityModel> ()->GetPosition ();
              outFile << "set label \"" << uedev->GetImsi ()
                      << "\" at "<< pos.x << "," << pos.y << " left font \"Helvetica,4\" textcolor rgb \"grey\" front point pt 1 ps 0.3 lc rgb \"grey\" offset 0,0"
                      << std::endl;
            }
        }
    }
}

void
PrintGnuplottableEnbListToFile (std::string filename)
{
  std::ofstream outFile;
  outFile.open (filename.c_str (), std::ios_base::out | std::ios_base::trunc);
  if (!outFile.is_open ())
    {
      NS_LOG_ERROR ("Can't open file " << filename);
      return;
    }
  for (NodeList::Iterator it = NodeList::Begin (); it != NodeList::End (); ++it)
    {
      Ptr<Node> node = *it;
      int nDevs = node->GetNDevices ();
      for (int j = 0; j < nDevs; j++)
        {
          Ptr<LteEnbNetDevice> enbdev = node->GetDevice (j)->GetObject <LteEnbNetDevice> ();
          if (enbdev)
            {
              Vector pos = node->GetObject<MobilityModel> ()->GetPosition ();
              outFile << "set label \"" << enbdev->GetCellId ()
                      << "\" at "<< pos.x << "," << pos.y
                      << " left font \"Helvetica,4\" textcolor rgb \"white\" front  point pt 2 ps 0.3 lc rgb \"white\" offset 0,0"
                      << std::endl;
            }
        }
    }
}


static ns3::GlobalValue g_nBlocks ("nBlocks",
                                   "Number of femtocell blocks",
                                   ns3::UintegerValue (0),
                                   ns3::MakeUintegerChecker<uint32_t> ());
static ns3::GlobalValue g_nApartmentsX ("nApartmentsX",
                                        "Number of apartments along the X axis in a femtocell block",
                                        ns3::UintegerValue (0),
                                        ns3::MakeUintegerChecker<uint32_t> ());
static ns3::GlobalValue g_nFloors ("nFloors",
                                   "Number of floors",
                                   ns3::UintegerValue (0),
                                   ns3::MakeUintegerChecker<uint32_t> ());
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
static ns3::GlobalValue g_areaMarginFactor ("areaMarginFactor",
                                            "how much the UE area extends outside the macrocell grid, "
                                            "expressed as fraction of the interSiteDistance",
                                            ns3::DoubleValue (0.5),
                                            ns3::MakeDoubleChecker<double> ());
static ns3::GlobalValue g_macroUeDensity ("macroUeDensity",
                                          "How many macrocell UEs there are per square meter",
                                          ns3::DoubleValue (0.00002),
                                          ns3::MakeDoubleChecker<double> ());
static ns3::GlobalValue g_homeEnbDeploymentRatio ("homeEnbDeploymentRatio",
                                                  "The HeNB deployment ratio as per 3GPP R4-092042",
                                                  ns3::DoubleValue (0.2),
                                                  ns3::MakeDoubleChecker<double> ());
static ns3::GlobalValue g_homeEnbActivationRatio ("homeEnbActivationRatio",
                                                  "The HeNB activation ratio as per 3GPP R4-092042",
                                                  ns3::DoubleValue (0.5),
                                                  ns3::MakeDoubleChecker<double> ());
static ns3::GlobalValue g_homeUesHomeEnbRatio ("homeUesHomeEnbRatio",
                                               "How many (on average) home UEs per HeNB there are in the simulation",
                                               ns3::DoubleValue (1.0),
                                               ns3::MakeDoubleChecker<double> ());
static ns3::GlobalValue g_macroEnbTxPowerDbm ("macroEnbTxPowerDbm",
                                              "TX power [dBm] used by macro eNBs",
                                              ns3::DoubleValue (43.0),
                                              ns3::MakeDoubleChecker<double> ());
static ns3::GlobalValue g_homeEnbTxPowerDbm ("homeEnbTxPowerDbm",
                                             "TX power [dBm] used by HeNBs",
                                             ns3::DoubleValue (20.0),
                                             ns3::MakeDoubleChecker<double> ());
static ns3::GlobalValue g_macroEnbDlEarfcn ("macroEnbDlEarfcn",
                                            "DL EARFCN used by macro eNBs",
                                            ns3::UintegerValue (100),
                                            ns3::MakeUintegerChecker<uint16_t> ());
static ns3::GlobalValue g_homeEnbDlEarfcn ("homeEnbDlEarfcn",
                                           "DL EARFCN used by HeNBs",
                                           ns3::UintegerValue (100),
                                           ns3::MakeUintegerChecker<uint16_t> ());
static ns3::GlobalValue g_macroEnbBandwidth ("macroEnbBandwidth",
                                             "bandwidth [num RBs] used by macro eNBs",
                                             ns3::UintegerValue (25),
                                             ns3::MakeUintegerChecker<uint16_t> ());
static ns3::GlobalValue g_homeEnbBandwidth ("homeEnbBandwidth",
                                            "bandwidth [num RBs] used by HeNBs",
                                            ns3::UintegerValue (25),
                                            ns3::MakeUintegerChecker<uint16_t> ());
static ns3::GlobalValue g_simTime ("simTime",
                                   "Total duration of the simulation [s]",
                                   ns3::DoubleValue (0.25),
                                   ns3::MakeDoubleChecker<double> ());
static ns3::GlobalValue g_generateRem ("generateRem",
                                       "if true, will generate a REM and then abort the simulation;"
                                       "if false, will run the simulation normally (without generating any REM)",
                                       ns3::BooleanValue (false),
                                       ns3::MakeBooleanChecker ());
static ns3::GlobalValue g_remRbId ("remRbId",
                                   "Resource Block Id of Data Channel, for which REM will be generated;"
                                   "default value is -1, what means REM will be averaged from all RBs of "
                                   "Control Channel",
                                   ns3::IntegerValue (-1),
                                   MakeIntegerChecker<int32_t> ());
static ns3::GlobalValue g_epc ("epc",
                               "If true, will setup the EPC to simulate an end-to-end topology, "
                               "with real IP applications over PDCP and RLC UM (or RLC AM by changing "
                               "the default value of EpsBearerToRlcMapping e.g. to RLC_AM_ALWAYS). "
                               "If false, only the LTE radio access will be simulated with RLC SM. ",
                               ns3::BooleanValue (true),
                               ns3::MakeBooleanChecker ());
static ns3::GlobalValue g_epcDl ("epcDl",
                                 "if true, will activate data flows in the downlink when EPC is being used. "
                                 "If false, downlink flows won't be activated. "
                                 "If EPC is not used, this parameter will be ignored.",
                                 ns3::BooleanValue (true),
                                 ns3::MakeBooleanChecker ());
static ns3::GlobalValue g_epcUl ("epcUl",
                                 "if true, will activate data flows in the uplink when EPC is being used. "
                                 "If false, uplink flows won't be activated. "
                                 "If EPC is not used, this parameter will be ignored.",
                                 ns3::BooleanValue (true),
                                 ns3::MakeBooleanChecker ());
static ns3::GlobalValue g_useUdp ("useUdp",
                                  "if true, the UdpClient application will be used. "
                                  "Otherwise, the BulkSend application will be used over a TCP connection. "
                                  "If EPC is not used, this parameter will be ignored.",
                                  ns3::BooleanValue (true),
                                  ns3::MakeBooleanChecker ());
static ns3::GlobalValue g_fadingTrace ("fadingTrace",
                                       "The path of the fading trace (by default no fading trace "
                                       "is loaded, i.e., fading is not considered)",
                                       ns3::StringValue (""),
                                       ns3::MakeStringChecker ());
static ns3::GlobalValue g_numBearersPerUe ("numBearersPerUe",
                                           "How many bearers per UE there are in the simulation",
                                           ns3::UintegerValue (1),
                                           ns3::MakeUintegerChecker<uint16_t> ());
static ns3::GlobalValue g_srsPeriodicity ("srsPeriodicity",
                                          "SRS Periodicity (has to be at least "
                                          "greater than the number of UEs per eNB)",
                                          ns3::UintegerValue (80),
                                          ns3::MakeUintegerChecker<uint16_t> ());
static ns3::GlobalValue g_outdoorUeMinSpeed ("outdoorUeMinSpeed",
                                             "Minimum speed value of macor UE with random waypoint model [m/s].",
                                             ns3::DoubleValue (0.0),
                                             ns3::MakeDoubleChecker<double> ());
static ns3::GlobalValue g_outdoorUeMaxSpeed ("outdoorUeMaxSpeed",
                                             "Maximum speed value of macor UE with random waypoint model [m/s].",
                                             ns3::DoubleValue (0.0),
                                             ns3::MakeDoubleChecker<double> ());

///////////////////////////////////////////////////////////////////////////

//static ns3::GlobalValue g_nmacroUes	("nUes",
//									"Number of user equipment",
//									ns3::UintegerValue(20),
//									ns3::MakeUintegerChecker<uint16_t> ());

static const uint16_t NUMBER_OF_UES = 105;
static const std::string PATH_PREFIX = "/home/tupevarj/NS3SimulatorData/";


///////////////////////////////////////////////////////////////////////////
//
//		CALLBACK TRACES
//
///////////////////////////////////////////////////////////////////////////

/*
 * Time start point in real life
 */
#ifdef DEBUG
clock_t timeStart; // = clock();
clock_t timePrevious; // = clock();
#endif //DEBUG

ConfigureInOut confInOut;

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


void
HandoverEndOkCallback(std::string context, uint64_t imsi,
                       uint16_t cellId, uint16_t rnti)
{
	//OutPutTraceII(PATH_PREFIX + "handover_log.csv", Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, "Handover End OK", cellId);
	confInOut.LogHandover(Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, HandoverStart, cellId, 0);
}


void
HandoverStartCallback(std::string context,
                       uint64_t imsi,
                       uint16_t cellid,
                       uint16_t rnti,
                       uint16_t targetCellId)
{
//	OutPutTraceII(PATH_PREFIX + "handover_log.csv", Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, "Handover Start", cellid, targetCellId);
	confInOut.LogHandover(Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, HandoverStart, cellid, targetCellId);
}

void
A2RsrqEnterCallback(std::string context,
					uint64_t imsi,
					uint16_t cellId,
					double rsrq)
{
//	OutPutTraceII(PATH_PREFIX + "event_log.csv", Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, "A2 RSRQ Enter", rsrq, cellId);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, A2RSRQEnter, cellId, rsrq);
}

void
A2RsrpEnterCallback(std::string context,
		uint64_t imsi,
		uint16_t cellId,
		double rsrq)
{
//	OutPutTraceII(PATH_PREFIX + "event_log.csv", Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, "A2 RSRP Enter", rsrq, cellId);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, A2RSRPEnter, cellId, rsrq);
}

void
A2RsrpLeaveCallback(std::string context,
						uint64_t imsi,
						uint16_t cellId,
						double rsr)
{
//	OutPutTraceII(PATH_PREFIX + "event_log.csv", Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, "A2 RSRP Leave", rsr, cellId);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, A2RSRPLeave, cellId, rsr);
}

void
A2RsrqLeaveCallback(std::string context,
						uint64_t imsi,
						uint16_t cellId,
						double rsr)
{
//	OutPutTraceII(PATH_PREFIX + "event_log.csv", Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, "A2 RSRQ Leave", rsr, cellId);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, A2RSRQLeave, cellId, rsr);
}

void
A3RsrpEnterCallback(std::string context,
				uint64_t imsi,
				uint16_t cellId,
				double rsrp)
{
	//OutPutTraceII(PATH_PREFIX + "event_log.csv", Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, "A3 RSRP Enter", rsrp, cellId);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, A3RSRPEnter, cellId, rsrp);
}

void
OutOfSynchCallback(std::string context,
					uint64_t imsi,
					uint16_t cellId,
					double rsrp,
					double thresh)
{
#ifdef DEBUG
	clock_t timeEnd = clock();
	double timeSpent = (double)(timeEnd - timeStart) / CLOCKS_PER_SEC;
	//confInOut.OutPutTrace(PATH_PREFIX + "EventLog.txt", Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, timeSpent, imsi, cellId, rsrp, "OoS");
#endif //DEBUG
	//OutPutTraceII(PATH_PREFIX + "event_log.csv", Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, "Out-of-synch", cellId, rsrp);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, OutOfSynch, cellId, rsrp);
}

void
RadioLinkFailureCallback(std::string context,
					uint64_t imsi,
					uint16_t cellId,
					double rsrp)
{
#ifdef DEBUG
	clock_t timeEnd = clock();
	double timeSpent = (double)(timeEnd - timeStart) / CLOCKS_PER_SEC;
	confInOut.OutPutTrace("event_log.csv", Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, timeSpent, imsi, cellId, rsrp, "RLF");
#endif //DEBUG
//	OutPutTraceII(PATH_PREFIX + "RLFS.csv", Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, "Radio Link Failure", cellId, rsrp);
	confInOut.LogEvent(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, RLF, cellId, rsrp);
}

void
KpiTestCallback(std::string context, uint64_t imsi, uint16_t cellId, double rsrp, double rsrq)
{
//	OutPutTraceII(PATH_PREFIX + "main_log.csv", Simulator::Now().GetSeconds(), (int)GetUeLocation(imsi).x, (int)GetUeLocation(imsi).y, imsi, cellId, rsrp, rsrq);
	confInOut.LogMainKpis(Simulator::Now().GetSeconds(), GetUeLocation(imsi).x, GetUeLocation(imsi).y, imsi, cellId, rsrp, rsrq);
}


///////////////////////////////////////////////////////////////////////////
// END:		CALLBACK TRACES AND DATA OUTPUT
///////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////
//
//		CONFIGURE SETTERS
//
///////////////////////////////////////////////////////////////////////////

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

///////////////////////////////////////////////////////////////////////////
// END:		CONFIGURE SETTERS
///////////////////////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//
//     		READING WRITING AND UPDATING CONF OUTDATA
//
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#define DEBUG

//static const char* CONFIGURATION_FILE = "configuration";
//static const char* OUTPUT_FILE = "data_out.txt";


void
GenerateRemMap(double xMin, double xMax, double yMin, double yMax)
{
	 Ptr<RadioEnvironmentMapHelper> remHelper;
     PrintGnuplottableUeListToFile (PATH_PREFIX + "REM_UES.csv");

	 remHelper = CreateObject<RadioEnvironmentMapHelper> ();
	 remHelper->SetAttribute ("ChannelPath", StringValue ("/ChannelList/0"));
	 remHelper->SetAttribute ("OutputFile", StringValue (PATH_PREFIX + "REM_DATA.csv"));
	 remHelper->SetAttribute ("XMin", DoubleValue (xMin));
	 remHelper->SetAttribute ("XMax", DoubleValue (xMax + 100));
	 remHelper->SetAttribute ("XRes", UintegerValue (275));
	 remHelper->SetAttribute ("YMin", DoubleValue (yMin));
	 remHelper->SetAttribute ("YMax", DoubleValue (yMax));
	 remHelper->SetAttribute ("YRes", UintegerValue (225));
	 remHelper->SetAttribute ("Z", DoubleValue (1.5));
	 remHelper->Install ();
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

#ifdef DEBUG
/* For DEBUGGING: writes random changes to configuration file */
void
TestWriteConfiguration()
{
//	static const double TEST_TX_POWERS[10] = { 21, 65, 99, 0, 12, 110, 46, 124, 88, 2 };
//
//	srand (time(NULL));
//	int randomNumber = rand() % 10;
////	ConfigurationData cd;
//
//	cd.txPower[0] = TEST_TX_POWERS[randomNumber];
//	cd.txPower[1] = TEST_TX_POWERS[randomNumber];

	//confInOut.TestWriteConfigurationFile(CONFIGURATION_FILE, cd);
}
#endif // DEBUG

static int fileNumber = 0;

/* Reads changes from configuration file and apply changes if updated */
void Update()
{
#ifdef DEBUG
	TestWriteConfiguration();
#endif // DEBUG

	ConfigurationLog conf = confInOut.ReadConfigurationFromDatabase();
//	if(ConfigurationLog conf = confInOut.ReadConfigurationFromDatabase())
//	{
		ApplyChanges(conf);
//	}
	std::stringstream strs;
	strs << fileNumber;
	std::string postFix = strs.str();

//	ConfigurationData conf = confInOut.ReadConfigurationFileCSV(PATH_PREFIX + "Configure/" + CONFIGURATION_FILE + postFix + ".csv");
	//OutPutTraceII(PATH_PREFIX + "test.csv", fileNumber, PATH_PREFIX + CONFIGURATION_FILE + postFix + ".csv", postFix, conf.txPower[11], conf.txPower[12], "");
	fileNumber++;
	//ApplyChanges(conf);
	// Schedule next update:
	Simulator::Schedule (MilliSeconds (3000), &Update);
}

void
CellOutage()
{
	SetCellTransmissionPower(10, 0.0);
	SetCellTransmissionPower(11, 0.0);
	SetCellTransmissionPower(12, 0.0);
}

//
//void Output(DataOut dOut)
//{
//	confInOut.WriteDataFile(OUTPUT_FILE, dOut);
//}

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


void
WriteUeThroughPut(Ptr<RadioBearerStatsCalculator> rlcStats)
{
	// last mesured throughput for Ues.
	static double lastThrs[NUMBER_OF_UES];

	for(int i = 1; i <= NUMBER_OF_UES; ++i)
	{
		double rxBytes = rlcStats->GetUlRxData(i , 4) * 0.001; // kilobytes		TODO: // SELVITÄ VIELÄ Logical Chanel ID   < LCID!
		double timeNow = Simulator::Now().GetSeconds();
		//OutPutTraceII(PATH_PREFIX + "throughput_log.csv", timeNow, i, GetConnectedCell(i), (rxBytes- lastThrs[i-1]) /0.200);

		confInOut.LogThroughput(timeNow, uint64_t(i), GetConnectedCell(i), (rxBytes- lastThrs[i-1]) /0.200);

		lastThrs[i-1] =  rxBytes;
	}
	Simulator::Schedule(MilliSeconds (200), &WriteUeThroughPut, rlcStats);
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// END:		READING WRITING AND UPDATING CONF OUTDATA
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


void
ReportUeSinr(double time, uint64_t imsi, uint16_t cellId, double sinr)
{
	confInOut.LogSinr(time, imsi, cellId, sinr);
}


int
main (int argc, char *argv[])
{
  // change some default attributes so that they are reasonable for
  // this scenario, but do this before processing command line
  // arguments, so that the user is allowed to override these settings
  Config::SetDefault ("ns3::UdpClient::Interval", TimeValue (MilliSeconds (1)));
  Config::SetDefault ("ns3::UdpClient::MaxPackets", UintegerValue (1000000));
  Config::SetDefault ("ns3::LteRlcUm::MaxTxBufferSize", UintegerValue (10 * 1024));


  ///////////////////////////////////////////////////////////////////////////
  //
  //	CHANGE MADE HERE:
  //		- ADDED DEFAULT VALUE FOR THRS RSRP
  //  SetCellTransmissionPower(10, 0.0);
  //  SetCellTransmissionPower(11, 0.0);
  //  SetCellTransmissionPower(12, 0.0);
  //
  ///////////////////////////////////////////////////////////////////////////

  Config::SetDefault("ns3::LteUeRrc::ThresholdRsrpLow", DoubleValue(-70));

  CommandLine cmd;
  cmd.Parse (argc, argv);
  ConfigStore inputConfig;
  inputConfig.ConfigureDefaults ();
  // parse again so you can override input file default values via command line
  cmd.Parse (argc, argv);


  // the scenario parameters get their values from the global attributes defined above
  UintegerValue uintegerValue;
  IntegerValue integerValue;
  DoubleValue doubleValue;
  BooleanValue booleanValue;
  StringValue stringValue;
  GlobalValue::GetValueByName ("nMacroEnbSites", uintegerValue);
  uint32_t nMacroEnbSites = uintegerValue.Get ();
  GlobalValue::GetValueByName ("nMacroEnbSitesX", uintegerValue);
  uint32_t nMacroEnbSitesX = uintegerValue.Get ();
  GlobalValue::GetValueByName ("interSiteDistance", doubleValue);
  double interSiteDistance = doubleValue.Get ();
  GlobalValue::GetValueByName ("areaMarginFactor", doubleValue);
  double areaMarginFactor = doubleValue.Get ();
  GlobalValue::GetValueByName ("macroEnbTxPowerDbm", doubleValue);
  double macroEnbTxPowerDbm = doubleValue.Get ();
  GlobalValue::GetValueByName ("macroEnbDlEarfcn", uintegerValue);
  uint16_t macroEnbDlEarfcn = uintegerValue.Get ();
  GlobalValue::GetValueByName ("macroEnbBandwidth", uintegerValue);
  uint16_t macroEnbBandwidth = uintegerValue.Get ();
  GlobalValue::GetValueByName ("simTime", doubleValue);
  double simTime = doubleValue.Get ();
  GlobalValue::GetValueByName ("epc", booleanValue);
  bool epc = booleanValue.Get ();
  GlobalValue::GetValueByName ("epcDl", booleanValue);
  bool epcDl = booleanValue.Get ();
  GlobalValue::GetValueByName ("epcUl", booleanValue);
  bool epcUl = booleanValue.Get ();
  GlobalValue::GetValueByName ("useUdp", booleanValue);
  bool useUdp = booleanValue.Get ();
  GlobalValue::GetValueByName ("generateRem", booleanValue);
  bool generateRem = booleanValue.Get ();
  GlobalValue::GetValueByName ("remRbId", integerValue);
  int32_t remRbId = integerValue.Get ();
  GlobalValue::GetValueByName ("fadingTrace", stringValue);
  std::string fadingTrace = stringValue.Get ();
  GlobalValue::GetValueByName ("numBearersPerUe", uintegerValue);
  uint16_t numBearersPerUe = uintegerValue.Get ();
  GlobalValue::GetValueByName ("srsPeriodicity", uintegerValue);
  uint16_t srsPeriodicity = uintegerValue.Get ();
  GlobalValue::GetValueByName ("outdoorUeMinSpeed", doubleValue);
  uint16_t outdoorUeMinSpeed = doubleValue.Get ();
  GlobalValue::GetValueByName ("outdoorUeMaxSpeed", doubleValue);
  uint16_t outdoorUeMaxSpeed = doubleValue.Get ();


  ///////////////////////////////////////////////////////////////////////////
  //
  //	CHANGE MADE HERE:
  //		- READ CONFIGURATION FILE
  //		- REAL-TIME
  //
  ///////////////////////////////////////////////////////////////////////////

//  confInOut.CreateConnectionToDataBase();
//  confInOut.SetDatabase("ns3_db");

  Config::SetDefault ("ns3::LteEnbRrc::SrsPeriodicity", UintegerValue (srsPeriodicity));

  Box macroUeBox;
  double ueZ = 1.5;
  if (nMacroEnbSites > 0)
    {
      uint32_t currentSite = nMacroEnbSites -1;
      uint32_t biRowIndex = (currentSite / (nMacroEnbSitesX + nMacroEnbSitesX + 1));
      uint32_t biRowRemainder = currentSite % (nMacroEnbSitesX + nMacroEnbSitesX + 1);
      uint32_t rowIndex = biRowIndex*2 + 1;
      if (biRowRemainder >= nMacroEnbSitesX)
        {
          ++rowIndex;
        }
      uint32_t nMacroEnbSitesY = rowIndex;
      NS_LOG_LOGIC ("nMacroEnbSitesY = " << nMacroEnbSitesY);

      macroUeBox = Box (-areaMarginFactor*interSiteDistance,
                        (nMacroEnbSitesX + areaMarginFactor)*interSiteDistance,
                        -areaMarginFactor*interSiteDistance,
                        (nMacroEnbSitesY -1)*interSiteDistance*sqrt (0.75) + areaMarginFactor*interSiteDistance,
                        ueZ, ueZ);
    }
  else
    {
      // still need the box to place femtocell blocks
      macroUeBox = Box (0, 150, 0, 150, ueZ, ueZ);
    }

  NodeContainer macroEnbs;
  macroEnbs.Create (3 * nMacroEnbSites);
  NodeContainer macroUes;
  macroUes.Create (NUMBER_OF_UES);

  MobilityHelper mobility;
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");


  Ptr <LteHelper> lteHelper = CreateObject<LteHelper> ();
  lteHelper->SetAttribute ("PathlossModel", StringValue ("ns3::HybridBuildingsPropagationLossModel"));
  lteHelper->SetPathlossModelAttribute ("ShadowSigmaOutdoor", DoubleValue (1));
  // use always LOS model
  lteHelper->SetPathlossModelAttribute ("Los2NlosThr", DoubleValue (1e6));
  lteHelper->SetSpectrumChannelType ("ns3::MultiModelSpectrumChannel");

  if (!fadingTrace.empty ())
    {
      lteHelper->SetAttribute ("FadingModel", StringValue ("ns3::TraceFadingLossModel"));
      lteHelper->SetFadingModelAttribute ("TraceFilename", StringValue (fadingTrace));
    }

  Ptr<PointToPointEpcHelper> epcHelper;
  if (epc)
    {
      NS_LOG_LOGIC ("enabling EPC");
      epcHelper = CreateObject<PointToPointEpcHelper> ();
      lteHelper->SetEpcHelper (epcHelper);
    }

  // Macro eNBs in 3-sector hex grid

  mobility.Install (macroEnbs);
  BuildingsHelper::Install (macroEnbs);
  Ptr<LteHexGridEnbTopologyHelper> lteHexGridEnbTopologyHelper = CreateObject<LteHexGridEnbTopologyHelper> ();
  lteHexGridEnbTopologyHelper->SetLteHelper (lteHelper);
  lteHexGridEnbTopologyHelper->SetAttribute ("InterSiteDistance", DoubleValue (interSiteDistance));
  lteHexGridEnbTopologyHelper->SetAttribute ("MinX", DoubleValue (interSiteDistance/2));
  lteHexGridEnbTopologyHelper->SetAttribute ("GridWidth", UintegerValue (nMacroEnbSitesX));
  Config::SetDefault ("ns3::LteEnbPhy::TxPower", DoubleValue (macroEnbTxPowerDbm));
  lteHelper->SetEnbAntennaModelType ("ns3::ParabolicAntennaModel");
  lteHelper->SetEnbAntennaModelAttribute ("Beamwidth",   DoubleValue (70));
  lteHelper->SetEnbAntennaModelAttribute ("MaxAttenuation",     DoubleValue (20.0));
  lteHelper->SetEnbDeviceAttribute ("DlEarfcn", UintegerValue (macroEnbDlEarfcn));
  lteHelper->SetEnbDeviceAttribute ("UlEarfcn", UintegerValue (macroEnbDlEarfcn + 18000));
  lteHelper->SetEnbDeviceAttribute ("DlBandwidth", UintegerValue (macroEnbBandwidth));
  lteHelper->SetEnbDeviceAttribute ("UlBandwidth", UintegerValue (macroEnbBandwidth));
  NetDeviceContainer macroEnbDevs = lteHexGridEnbTopologyHelper->SetPositionAndInstallEnbDevice (macroEnbs);

  if (epc)
    {
      // this enables handover for macro eNBs
      lteHelper->AddX2Interface (macroEnbs);
    }

  Ptr<PositionAllocator> positionAlloc = CreateObject<RandomRoomPositionAllocator> ();
  mobility.SetPositionAllocator (positionAlloc);
  lteHelper->SetUeDeviceAttribute ("CsgId", UintegerValue (1));

  // macro Ues
  NS_LOG_LOGIC ("randomly allocating macro UEs in " << macroUeBox << " speedMin " << outdoorUeMinSpeed << " speedMax " << outdoorUeMaxSpeed);
  if (outdoorUeMaxSpeed!=0.0)
    {
      mobility.SetMobilityModel ("ns3::SteadyStateRandomWaypointMobilityModel");

      Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::MinX", DoubleValue (macroUeBox.xMin));
      Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::MinY", DoubleValue (macroUeBox.yMin));
      Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::MaxX", DoubleValue (macroUeBox.xMax));
      Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::MaxY", DoubleValue (macroUeBox.yMax));
      Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::Z", DoubleValue (ueZ));
      Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::MaxSpeed", DoubleValue (outdoorUeMaxSpeed));
      Config::SetDefault ("ns3::SteadyStateRandomWaypointMobilityModel::MinSpeed", DoubleValue (outdoorUeMinSpeed));

      positionAlloc = CreateObject<RandomBoxPositionAllocator> ();
      mobility.SetPositionAllocator (positionAlloc);
      mobility.Install (macroUes);

      for (NodeContainer::Iterator it = macroUes.Begin ();
           it != macroUes.End ();
           ++it)
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


  NetDeviceContainer macroUeDevs = lteHelper->InstallUeDevice (macroUes);

  Ipv4Address remoteHostAddr;
  NodeContainer ues;
  Ipv4StaticRoutingHelper ipv4RoutingHelper;
  Ipv4InterfaceContainer ueIpIfaces;
  Ptr<Node> remoteHost;
  NetDeviceContainer ueDevs;

  if (epc)
    {
      NS_LOG_LOGIC ("setting up internet and remote host");

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

      Ipv4StaticRoutingHelper ipv4RoutingHelper;
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
    }
  else
    {
      // macro UEs attached to the closest macro eNB
      lteHelper->AttachToClosestEnb (macroUeDevs, macroEnbDevs);
    }

  if (epc)
    {
      NS_LOG_LOGIC ("setting up applications");

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

          for (uint32_t b = 0; b < numBearersPerUe; ++b)
            {
              ++dlPort;
              ++ulPort;

              ApplicationContainer clientApps;
              ApplicationContainer serverApps;

              if (useUdp)
                {
                  if (epcDl)
                    {
                      NS_LOG_LOGIC ("installing UDP DL app for UE " << u);
                      UdpClientHelper dlClientHelper (ueIpIfaces.GetAddress (u), dlPort);
                      clientApps.Add (dlClientHelper.Install (remoteHost));
                      PacketSinkHelper dlPacketSinkHelper ("ns3::UdpSocketFactory",
                                                           InetSocketAddress (Ipv4Address::GetAny (), dlPort));
                      serverApps.Add (dlPacketSinkHelper.Install (ue));
                    }
                  if (epcUl)
                    {
                      NS_LOG_LOGIC ("installing UDP UL app for UE " << u);
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
                      NS_LOG_LOGIC ("installing TCP DL app for UE " << u);
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
                      NS_LOG_LOGIC ("installing TCP UL app for UE " << u);
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
  else // (epc == false)
    {
      // for radio bearer activation purposes, consider together home UEs and macro UEs
      NetDeviceContainer ueDevs;
     // ueDevs.Add (homeUeDevs);
      ueDevs.Add (macroUeDevs);
      for (uint32_t u = 0; u < ueDevs.GetN (); ++u)
        {
          Ptr<NetDevice> ueDev = ueDevs.Get (u);
          for (uint32_t b = 0; b < numBearersPerUe; ++b)
            {
              enum EpsBearer::Qci q = EpsBearer::NGBR_VIDEO_TCP_DEFAULT;
              EpsBearer bearer (q);
              lteHelper->ActivateDataRadioBearer (ueDev, bearer);
            }
        }
    }


  BuildingsHelper::MakeMobilityModelConsistent ();

  Ptr<RadioEnvironmentMapHelper> remHelper;
  if (generateRem)
    {
      PrintGnuplottableBuildingListToFile ("buildings.txt");
      PrintGnuplottableEnbListToFile ("enbs.txt");
      PrintGnuplottableUeListToFile (PATH_PREFIX + "REM_UES.csv");

      remHelper = CreateObject<RadioEnvironmentMapHelper> ();
      remHelper->SetAttribute ("ChannelPath", StringValue ("/ChannelList/0"));
      remHelper->SetAttribute ("OutputFile", StringValue (PATH_PREFIX + "REM_DATA.csv"));
      remHelper->SetAttribute ("XMin", DoubleValue (macroUeBox.xMin));
      remHelper->SetAttribute ("XMax", DoubleValue (macroUeBox.xMax + 100));
      remHelper->SetAttribute ("XRes", UintegerValue (825));
      remHelper->SetAttribute ("YMin", DoubleValue (macroUeBox.yMin));
      remHelper->SetAttribute ("YMax", DoubleValue (macroUeBox.yMax));
      remHelper->SetAttribute ("YRes", UintegerValue (675));
      remHelper->SetAttribute ("Z", DoubleValue (1.5));

      if (remRbId >= 0)
        {
          remHelper->SetAttribute ("UseDataChannel", BooleanValue (true));
          remHelper->SetAttribute ("RbId", IntegerValue (remRbId));
        }

      remHelper->Install ();
    //  confInOut.RunMatlabRemScript();
      // simulation will stop right after the REM has been generated
    }
  else
    {
      Simulator::Stop (Seconds (simTime));
    }

  lteHelper->EnableMacTraces ();
  lteHelper->EnableRlcTraces ();
  if (epc)
    {
      lteHelper->EnablePdcpTraces ();
    }

  ///////////////////////////////////////////////////////////////////////////
  //	CHANGE MADE HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  ///////////////////////////////////////////////////////////////////////////

//
//  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/HandoverEndOk",
//                     MakeCallback (&NotifyHandoverEndOkUe));
//
  lteHelper->EnablePhyTraces ();
  lteHelper->EnableDlPhyTraces();
  lteHelper->EnableUlPhyTraces();


  //////////////////////////////////////////////////////!!!!!!!!!!
  //lteHelper->EnableKpiTraces();

  Ptr<RadioBearerStatsCalculator> rlcStats = lteHelper->GetRlcStats ();
  rlcStats->SetAttribute ("StartTime", TimeValue (Seconds (0)));
  rlcStats->SetAttribute ("EpochDuration", TimeValue (Seconds (simTime)));



  Simulator::Schedule(MilliSeconds (200), &WriteUeThroughPut, rlcStats);
  Simulator::Schedule(MilliSeconds(7000), &CellOutage);
  // First update
//  Simulator::Schedule (MilliSeconds (3000), &Update);

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


 // EVENT LOG FILE CALLBACK

  // RLF
  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/RadioLinkFailure",
                    MakeCallback (&RadioLinkFailureCallback));

  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/OutOfSynch",
                    MakeCallback (&OutOfSynchCallback));

  // A2
  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/A2RsrqEnter",
                        MakeCallback (&A2RsrqEnterCallback));

  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/A2RsrqLeave",
                        MakeCallback (&A2RsrqLeaveCallback));

  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/A2RsrpLeave",
                        MakeCallback (&A2RsrpLeaveCallback));

  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/A2RsrpEnter",
                        MakeCallback (&A2RsrpEnterCallback));

  // A3
  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/A3Rsrp",
                        MakeCallback (&A3RsrpEnterCallback));

  // Handovers
  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/HandoverStart",
                        MakeCallback (&HandoverStartCallback));

  Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/HandoverEndOk",
                        MakeCallback (&HandoverEndOkCallback));

  // Main File
  Config::Connect("/NodeList/*/DeviceList/*/LteUeRrc/KpiTest",
		  	  	  MakeCallback(&KpiTestCallback));


  Ptr<PhyStatsCalculator> phyStats = lteHelper->GetPhyStatsCalculator();

  phyStats->TraceConnectWithoutContext("SinrTrace", MakeCallback(&ReportUeSinr));


 // confInOut.RunMatlabScript();

//  confInOut.ReadConfigurationFromDatabase();
//
//#ifdef DEBUG
//  timeStart = clock();
//  timePrevious = timeStart;
//#endif //DEBUG

  ///////////////////////////////////////////////////////////////////////////
   //	CHANGE MADE HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   ///////////////////////////////////////////////////////////////////////////

   double tx = 10.0;
   double changed_tx = 10.0;

   SetCellTransmissionPower(1, changed_tx);
   SetCellTransmissionPower(2, changed_tx);
   SetCellTransmissionPower(3, tx);
   SetCellTransmissionPower(4, tx);
   SetCellTransmissionPower(5, changed_tx);
   SetCellTransmissionPower(6, tx);
   SetCellTransmissionPower(7, changed_tx);
   SetCellTransmissionPower(8, tx);
   SetCellTransmissionPower(9, tx);

   SetCellTransmissionPower(10, 10.0);
   SetCellTransmissionPower(11, 10.0);
   SetCellTransmissionPower(12, 10.0);

   SetCellTransmissionPower(13, tx);
   SetCellTransmissionPower(14, changed_tx);
   SetCellTransmissionPower(15, changed_tx);
   SetCellTransmissionPower(16, changed_tx);
   SetCellTransmissionPower(17, tx);
   SetCellTransmissionPower(18, changed_tx);
   SetCellTransmissionPower(19, tx);
   SetCellTransmissionPower(20, tx);
   SetCellTransmissionPower(21, changed_tx);


  Simulator::Run ();

  //GenerateRemMap(macroUeBox.xMin, macroUeBox.xMax, macroUeBox.yMin, macroUeBox.yMax);

//
//#ifdef DEBUG
//	clock_t timeEnd = clock();
//	double timeSpent = (double)(timeEnd - timeStart) / CLOCKS_PER_SEC;
//	confInOut.OutPutTrace("testTime.txt", Simulator::Now().GetSeconds(), timeSpent, "", "", "", "RLF");
//#endif //DEBUG


  confInOut.FlushLogs();

  //GtkConfigStore config;
  //config.ConfigureAttributes ();
  confInOut.RunMatlabKpiScript();
//  confInOut.RunMatlabRemScript();
  lteHelper = 0;
  Simulator::Destroy ();

  return 0;
}

/*

./waf --run="LTE_test_opt --simTime=3 --nBlocks=0 --nMacroEnbSites=7 --nMacroEnbSitesX=2 --epc=1 --useUdp=0 --outdoorUeMinSpeed=16.6667 --outdoorUeMaxSpeed=16.6667 --ns3::LteHelper::HandoverAlgorithm=ns3::A3RsrpHandoverAlgorithm --ns3::RadioBearerStatsCalculator::DlRlcOutputFilename=a3-rsrp-DlRlcStats_START.txt --ns3::RadioBearerStatsCalculator::UlRlcOutputFilename=a3-rsrp-UlRlcStats_START.txt --ns3::PhyStatsCalculator::DlRsrpSinrFilename=a3-rsrp-DlRsrpSinrStats_START.txt --ns3::PhyStatsCalculator::UlSinrFilename=/home/tupevarj/NS3SimulatorData/main_log2.csv --RngRun=1" > a3-rsrp_START.txt
./waf --run="LTE_test_opt --simTime=3 --nBlocks=0 --nMacroEnbSites=7 --nMacroEnbSitesX=2 --epc=1 --useUdp=0 --outdoorUeMinSpeed=16.6667 --outdoorUeMaxSpeed=16.6667 --ns3::LteHelper::HandoverAlgorithm=ns3::A3RsrpHandoverAlgorithm"

./waf --run="lena-dual-stripe --simTime=10 --nBlocks=0 --nMacroEnbSites=7 --nMacroEnbSitesX=2 --epc=1 --useUdp=0 --outdoorUeMinSpeed=16.6667 --outdoorUeMaxSpeed=16.6667 --ns3::LteHelper::HandoverAlgorithm=ns3::A3RsrpHandoverAlgorithm --ns3::RadioBearerStatsCalculator::DlRlcOutputFilename=a3-rsrp-DlRlcStats.txt --ns3::RadioBearerStatsCalculator::UlRlcOutputFilename=a3-rsrp-UlRlcStats.txt --RngRun=1" > a3-rsrp.txt

 */
