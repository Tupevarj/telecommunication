/*
 * REMgenerator.cc
 *
 *  Created on: 12.1.2018
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

ConfigureInOut confInOut;

using namespace ns3;
int32_t PID = 0;

const int NUMBER_OF_UES = 20;

void
GenerateRemMap(Ptr<RadioEnvironmentMapHelper> remHelper, Box macroUeBox)
{
	remHelper->SetAttribute ("ChannelPath", StringValue ("/ChannelList/0"));
	remHelper->SetAttribute ("OutputFile", StringValue ("CSONREM.rem"));
	remHelper->SetAttribute ("XMin", DoubleValue (macroUeBox.xMin));
	remHelper->SetAttribute ("XMax", DoubleValue (macroUeBox.xMax));
	remHelper->SetAttribute ("YMin", DoubleValue (macroUeBox.yMin));
	remHelper->SetAttribute ("YMax", DoubleValue (macroUeBox.yMax));
	remHelper->SetAttribute ("XRes", UintegerValue (150));
	remHelper->SetAttribute ("YRes", UintegerValue (150));
	remHelper->SetAttribute ("Z", DoubleValue (1.5));
    remHelper->Install();
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


void
RemCallback(double x, double y, double z, double sinr)
{
	confInOut.LogREM(x, y, z, sinr);
}

void
RemEndedCallback(bool b)
{
	if(PID != 0)
		kill((pid_t)PID, SIGUSR1);
}


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//		GLOBAL VALUES
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

static ns3::GlobalValue g_step ("step",
                                   "Current step to be read from database for REM generating",
                                   ns3::UintegerValue (0),
                                   ns3::MakeUintegerChecker<uint32_t> ());


int
main (int argc, char *argv[])
{
		CommandLine cmd;
		cmd.Parse (argc, argv);
		ConfigStore inputConfig;
		inputConfig.ConfigureDefaults ();
		// parse again so you can override input file default values via command line
		cmd.Parse (argc, argv);

		UintegerValue uintegerValue;
		GlobalValue::GetValueByName ("step", uintegerValue);
		uint32_t step = uintegerValue.Get();

//		std::cout << "Started to generate REM, step: " << step << std::endl;

		///////////////////////////////////////////////
		// CONNECT TO DATABASE
		///////////////////////////////////////////////

		confInOut.CreateConnectionToDataBase();
		confInOut.SetDatabase("5gopt");

		///////////////////////////////////////////////
		// READ CONFIGURATION FROM DATABASE
		///////////////////////////////////////////////

		bool epc = true;
		uint32_t nMacroEnbSites;
		uint32_t nMacroEnbSitesX;
		double interSiteDistance;
		int32_t pid;

		confInOut.ReadSimulationState(nMacroEnbSites, nMacroEnbSitesX, interSiteDistance, pid);

		//std::cout << "Macro site: " << nMacroEnbSites << " X: " << nMacroEnbSitesX << std::endl;
		PID = pid;

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
			//todo: Probably not needed
			DemoHelper::NoEPC();
		}

		/////////////////////////////////////////////////////
		// READ CELLS TRANSMISSION POWERS FROM DATABASE
		/////////////////////////////////////////////////////
		int noCells = 3 * nMacroEnbSites;
		double txs[noCells + 1];

		confInOut.ReadCellsStates(txs, noCells, step);
//		std::cout << "Step: " << step << std::endl;

		for(int i = 1; i < noCells+1; i++)
		{
			SetCellTransmissionPower(i, txs[i]);
		}
	//	lteHelper->EnablePhyTraces ();
	//	lteHelper->EnableDlPhyTraces();
	//	lteHelper->EnableUlPhyTraces();
	//	lteHelper->EnableMacTraces ();
	//	lteHelper->EnableRlcTraces ();
	//	lteHelper->EnablePdcpTraces ();

	//	/* Generating REMs */
		Ptr<RadioEnvironmentMapHelper> remHelper;
		remHelper = CreateObject<RadioEnvironmentMapHelper> ();
		remHelper->TraceConnectWithoutContext("RemTrace", MakeCallback(&RemCallback));
		remHelper->TraceConnectWithoutContext("RemEndedTrace", MakeCallback(&RemEndedCallback));
		// Generate REM
		GenerateRemMap(remHelper, macroUeBox);

		Simulator::Run ();

		std::ostringstream ss;
		ss << step;

		confInOut.SetPostFixCSV(ss.str());
		confInOut.FlushLogs();
		std::cout << "  REM is written to DB" << std::endl;


		//kill((pid_t)pid, SIGUSR1);

		lteHelper = 0;
		Simulator::Destroy ();
}

/*
	./waf --run="REMgenerator"
*/
