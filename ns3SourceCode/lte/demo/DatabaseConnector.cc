#include "DatabaseConnector.h"

#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <ios>
#include <cstdlib>
#include <string>
#include <mongocxx/cursor.hpp>
#include <unistd.h>
#include <time.h>

DatabaseConnector::DatabaseConnector() : mongoClient(NULL), mongoDatabase(NULL), mongoCollection(NULL)
{

}

const std::string CurrentDateTime() {
    time_t     now = time(0);
    struct tm  tstruct;
    char       buf[80];
    tstruct = *localtime(&now);
    strftime(buf, sizeof(buf), "%Y-%m-%d.%X", &tstruct);

    return buf;
}


////////////////////////////////////////////////////////////////////////////////////
//	MONGO DB
////////////////////////////////////////////////////////////////////////////////////


/* HUOM!!! Skripti ei toimi vielä: --dbpath ei toimi */
void
DatabaseConnector::CreateConnectionToDataBase()
{
	// RunMongoStartScript();
	mongocxx::instance inst{};
	mongoClient = new mongocxx::client{mongocxx::uri{}};
}


void
DatabaseConnector::SetDatabase(std::string db)
{
	mongoDatabase = new mongocxx::database{mongoClient->database(db)};
}

void
DatabaseConnector::SetCollection(std::string coll)
{
	mongoCollection = new mongocxx::collection{mongoDatabase->collection(coll)};
}

void
DatabaseConnector::TestWriteToCurrentCollection()
{
	bsoncxx::builder::stream::document document{};
	document << "name:" << "Tuukka" << "lastName" << "Varjus";

	mongoCollection->insert_one(document.view());
}


void DatabaseConnector::LogStatus(std::string sim_time, std::string message, int type)
{
	statusLog.push_back(StatusLog("[" + CurrentDateTime() + "] (" + sim_time + ")", "   " + message, type));
}


void
DatabaseConnector::LogEvent(double time, double x, double y,uint64_t imsi, EventName e, uint16_t cellId, double rsr)
{
	eventsLog.push_back(EventLog{time, x, y, rsr, imsi, cellId, e});
//	eventsLogCol.AddLog(new EventLog{time, x, y, rsr, imsi, cellId, e});
}

void
DatabaseConnector::LogHandover(double time, double x, double y,uint64_t imsi, HandoverEventName e, uint16_t cellId, uint16_t targetCellId)
{
	handoversLog.push_back(HandoverLog{time, x, y, imsi, cellId, targetCellId, e});
	//handoversLogCol.AddLog(new HandoverLog{time, x, y, imsi, cellId, targetCellId, e});
}

void
DatabaseConnector::LogSinr(double time, uint64_t imsi, uint16_t cellId, double sinr)
{
	//sinrsLogCol.AddLog(new SinrLog{time, sinr, imsi, cellId});
	sinrsLog.push_back(SinrLog{time, sinr, imsi, cellId});
}

void
DatabaseConnector::LogThroughput(double time, uint64_t imsi, uint16_t cellId, double thr)
{
//	throughputsLogCol.AddLog(new ThrouhgputLog{time, thr, imsi, cellId});
	throughputsLog.push_back(ThrouhgputLog{time, thr, imsi, cellId});
}

void
DatabaseConnector::LogMainKpisWithLabeling(double time, double x, double y, uint64_t imsi, uint16_t cellId, double rsrp, double rsrq, bool connected, bool label)
{
	mainKpisWithLabelLog.push_back(MainKpiWithLabelLog{time, x, y, rsrp, rsrq, imsi, cellId, connected, label});
}

void
DatabaseConnector::LogMainKpis(double time, double x, double y, uint64_t imsi, uint16_t cellId, double rsrp, double rsrq, bool connected)
{
//	mainKpisLogCol.AddLog(new MainKpiLog{time, x, y, rsrp, rsrq, imsi, cellId});
	mainKpisLog.push_back(MainKpiLog{time, x, y, rsrp, rsrq, imsi, cellId, connected});
}

void
DatabaseConnector::LogREM(double x, double y, double z, double sinr)
{
	remLog.push_back(REMLog{x, y, z, sinr});
}

//
//void
//ConfigureInOut::WriteLogToCSVFile(std::string path, LogCollection logCol)
//{
//	std::ofstream outFile;
//	for(uint i = 0; i < logCol.logs.size(); ++i)
//	{
//		outFile.open(path.c_str(), std::ios_base::app);
//		outFile	<< logCol.logs[i]->ConvertToCSV() << "\n";
//	}
//	outFile.close();
//}
//

void
DatabaseConnector::WriteAllLogsToCSVFiles(std::string prefix)
{
	if(eventsLog.size() > 0)
	{
		std::ofstream outFile;
		outFile.open((prefix + EventLog::GetFileName() + postFix + ".csv").c_str(), std::ios_base::app);
		for(uint i = 0; i < eventsLog.size(); ++i)
		{
			outFile	<< eventsLog[i].ConvertToCSV() << "\n";
		}
		outFile.close();
	}
	if(handoversLog.size() > 0)
	{
		std::ofstream outFile;
		outFile.open((prefix + HandoverLog::GetFileName() + postFix + ".csv").c_str(), std::ios_base::app);
		for(uint i = 0; i < handoversLog.size(); ++i)
		{
			outFile	<< handoversLog[i].ConvertToCSV() << "\n";
		}
		outFile.close();
	}
	if(sinrsLog.size() > 0)
	{
		std::ofstream outFile;
		outFile.open((prefix + SinrLog::GetFileName() + postFix + ".csv").c_str(), std::ios_base::app);
		for(uint i = 0; i < sinrsLog.size(); ++i)
		{
			outFile	<< sinrsLog[i].ConvertToCSV() << "\n";
		}
		outFile.close();
	}
	if(throughputsLog.size() > 0)
	{
		std::ofstream outFile;
		outFile.open((prefix + ThrouhgputLog::GetFileName() + postFix + ".csv").c_str(), std::ios_base::app);
		for(uint i = 0; i < throughputsLog.size(); ++i)
		{
			outFile	<< throughputsLog[i].ConvertToCSV() << "\n";
		}
		outFile.close();
	}
	if(mainKpisLog.size() > 0)
	{
		std::ofstream outFile;
		outFile.open((prefix + MainKpiLog::GetFileName() + postFix + ".csv").c_str(), std::ios_base::app);
		for(uint i = 0; i < mainKpisLog.size(); ++i)
		{
			outFile	<< mainKpisLog[i].ConvertToCSV() << "\n";
		}
		outFile.close();
	}
	if(mainKpisWithLabelLog.size() > 0)
	{
		std::ofstream outFile;
		outFile.open((prefix + MainKpiWithLabelLog::GetFileName() + postFix + ".csv").c_str(), std::ios_base::app);
		for(uint i = 0; i < mainKpisWithLabelLog.size(); ++i)
		{
			outFile	<< mainKpisWithLabelLog[i].ConvertToCSV() << "\n";
		}
		outFile.close();
	}
	if(remLog.size() > 0)
	{
		std::ofstream outFile;
		outFile.open((prefix + REMLog::GetFileName() + postFix + ".csv").c_str(), std::ios_base::app);
		for(uint i = 0; i < remLog.size(); ++i)
		{
			outFile	<< remLog[i].ConvertToCSV() << "\n";
		}
		outFile.close();
	}
}

void
DatabaseConnector::WriteLogsToDatabase()
{
//	std::string no = "0";
	std::vector<bsoncxx::document::value> documents;

	/* EVENTS */
	if(eventsLog.size() > 0)
	{
		SetCollection("event_log");

		for(uint i = 0; i < eventsLog.size(); ++i)
		{
			documents.push_back(eventsLog[i].ConvertToBSON() << bsoncxx::builder::stream::finalize);
		}
		mongoCollection->insert_many(documents);
		documents.clear();
	}

	/* HANDOVERS */
	if(handoversLog.size() > 0)
	{
		SetCollection("handover_log");

		for(uint i = 0; i < handoversLog.size(); ++i)
		{
			documents.push_back(handoversLog[i].ConvertToBSON() << bsoncxx::builder::stream::finalize);
		}
		mongoCollection->insert_many(documents);
		documents.clear();
	}

	/* SINR */
	if(sinrsLog.size() > 0)
	{
		SetCollection("sinr_log");

		for(uint i = 0; i < sinrsLog.size(); ++i)
		{
			documents.push_back(sinrsLog[i].ConvertToBSON() << bsoncxx::builder::stream::finalize);
		}
		mongoCollection->insert_many(documents);
		documents.clear();
	}

	/* THROUGHPUTS */
	if(throughputsLog.size() > 0)
	{
		SetCollection("throughput_log");

		for(uint i = 0; i < throughputsLog.size(); ++i)
		{
			documents.push_back(throughputsLog[i].ConvertToBSON() << bsoncxx::builder::stream::finalize);
		}
		mongoCollection->insert_many(documents);
		documents.clear();
	}

	/* MAIN KPIS */
	if(mainKpisLog.size() > 0)
	{
		SetCollection("main_kpis_log");

		for(uint i = 0; i < mainKpisLog.size(); ++i)
		{
			documents.push_back(mainKpisLog[i].ConvertToBSON() << bsoncxx::builder::stream::finalize);
		}
		mongoCollection->insert_many(documents);
		documents.clear();
	}

	/* MAIN KPIS WITH LABELS */
	if(mainKpisWithLabelLog.size() > 0)
	{
		SetCollection("main_kpis_log");

		for(uint i = 0; i < mainKpisWithLabelLog.size(); ++i)
		{
			documents.push_back(mainKpisWithLabelLog[i].ConvertToBSON() << bsoncxx::builder::stream::finalize);
		}
		mongoCollection->insert_many(documents);
		documents.clear();
	}

	/* REM */
	if(remLog.size() > 0)
	{
		SetCollection("rem_log");

		for(uint i = 0; i < remLog.size(); ++i)
		{
			documents.push_back(remLog[i].ConvertToBSON() << bsoncxx::builder::stream::finalize);
		}
		mongoCollection->insert_many(documents);
		documents.clear();
	}

	/* STATUS */
	if(statusLog.size() > 0)
	{
		SetCollection("status_log");

		for(uint i = 0; i < statusLog.size(); ++i)
		{
			documents.push_back(statusLog[i].ConvertToBSON() << bsoncxx::builder::stream::finalize);
		}
		mongoCollection->insert_many(documents);
		documents.clear();
	}
}

SONEngineLog
DatabaseConnector::ReadSONEngineMethodsFromDatabase()
{
	while(!IsDatabaseUnlocked())
	{
		usleep(100);
	}
	LockDatabase();
	SetCollection("controlpanel");
	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << "outage" << 1 << "dirty_flag" << 0 << bsoncxx::builder::stream::finalize);


	SONEngineLog configuration =  SONEngineLog(cursor);

	/* UPDATE DIRTY FLAGS */
	bsoncxx::stdx::optional<mongocxx::result::update> result =
			mongoCollection->update_many(bsoncxx::builder::stream::document{} << "dirty_flag" << 0 << bsoncxx::builder::stream::finalize,
					bsoncxx::builder::stream::document{} << "$set" << bsoncxx::builder::stream::open_document << "dirty_flag" << 1 <<
					bsoncxx::builder::stream::close_document << bsoncxx::builder::stream::finalize);
	UnlockDatabase();


	return configuration;
//	}
}

/* todo: Check connection to database! SIGSEGV Error jos MongoDB ei ole käynnissä!!!!!!!!!!!!!! */
ConfigurationLog
DatabaseConnector::ReadConfigurationFromDatabase()
{
	while(!IsDatabaseUnlocked())
	{
		usleep(100);
	}
	LockDatabase();
	//int confNo = 0;// todo: GetConfigurationNumber() ++
//
	//SetDatabase("CellConfigurations");
	SetCollection("cell_configurations");

//
//	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << "Step" << confNo << bsoncxx::builder::stream::finalize);

	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << bsoncxx::builder::stream::finalize);
	ConfigurationLog configuration =  ConfigurationLog(cursor);
	UnlockDatabase();
	//TODO: SET LAST DATABASE
	//SetDatabase("5gopt");
	return configuration;
}


void
DatabaseConnector::UpdateTxPower(u_int16_t cellId, double tx)
{
	while(!IsDatabaseUnlocked())
	{
		usleep(100);
	}
	LockDatabase();
	//SetDatabase("CellConfigurations");
	SetCollection("cell_configurations");
	// Update
	mongoCollection->update_one(bsoncxx::builder::stream::document{} << "CellID" << cellId << bsoncxx::builder::stream::finalize,
				bsoncxx::builder::stream::document{} << "$set" << bsoncxx::builder::stream::open_document <<
				"TxPower" << tx << bsoncxx::builder::stream::close_document << bsoncxx::builder::stream::finalize);

	UnlockDatabase();
	//SetDatabase("5gopt");
}

bool
DatabaseConnector::CheckConnectionToDatabase()
{
	// todo: Check connection, relevant?
	return true;
}


void
DatabaseConnector::SetOutPutFolder(std::string path)
{
	outputFolder = path;
}


bool
DatabaseConnector::IsDatabaseUnlocked()
{
	//SetDatabase("5gopt");
	SetCollection("locks");
	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << bsoncxx::builder::stream::finalize);
	int count = 0;
	for(auto view : cursor)
	{
		count++;
		auto type = view["Type"];
		auto timeStamp = view["Time"];

		int t = type.get_int32();
		time_t time = std::time(0);
		int time_diffence = 0;

		try
		{
			time_diffence = time - timeStamp.get_int32();
		}
		catch(int e)
		{
			time_diffence = time - timeStamp.get_int64();
		}

		if(t == 0 || time_diffence > 5) return true;		// max lock time is 5 seconds
	}
	if(count == 0) return true;
	return false;
}

void
DatabaseConnector::LockDatabase()
{
	//SetDatabase("5gopt");
	SetCollection("locks");

	time_t time = std::time(0);

	mongocxx::options::update options;
    options.upsert(true);

	mongoCollection->update_one(bsoncxx::builder::stream::document{} << bsoncxx::builder::stream::finalize,
	bsoncxx::builder::stream::document{} << "$set" << bsoncxx::builder::stream::open_document << "Type" << 1 << "Time" << int(time) <<
	bsoncxx::builder::stream::close_document << bsoncxx::builder::stream::finalize, options);
}


void
DatabaseConnector::UnlockDatabase()
{
	SetDatabase("5gopt");
	SetCollection("locks");

	mongoCollection->update_one(bsoncxx::builder::stream::document{} << bsoncxx::builder::stream::finalize,
	bsoncxx::builder::stream::document{} << "$set" << bsoncxx::builder::stream::open_document << "Type" << 0 <<
	bsoncxx::builder::stream::close_document << bsoncxx::builder::stream::finalize);
}

void
DatabaseConnector::FlushLogs()
{
	if(mongoClient)
	{
		// TODO:
		while(!IsDatabaseUnlocked())
		{
			usleep(100);
		}
		LockDatabase();
		WriteLogsToDatabase();
		WriteAllLogsToCSVFiles(outputFolder); // <- DEBUG
		ClearAllLogs();
		UnlockDatabase();
	}
	else
	{
		WriteAllLogsToCSVFiles(outputFolder);
		ClearAllLogs();
	}
}


void
DatabaseConnector::SetPostFixCSV(std::string postFix)
{
	this->postFix = postFix;
}

void
DatabaseConnector::InitializeCellConfigurations(double txPower, int noCells, std::vector<std::vector<int>> cellLocations)
{
	while(!IsDatabaseUnlocked())
	{
		usleep(100);
	}
	LockDatabase();

//	SetDatabase("CellConfigurations");
	SetCollection("cell_configurations");
	//mongoCollection->drop();

	std::vector<bsoncxx::document::value> documents;

	for(int i = 1; i <= noCells; i++)
	{
		bsoncxx::builder::stream::document doc {};
		doc << "CellID" << i << "TxPower" << txPower << "LocationX" << cellLocations[i][0] << "LocationY" << cellLocations[i][1];
		documents.push_back(doc << bsoncxx::builder::stream::finalize);
	}
	mongoCollection->insert_many(documents);
	UnlockDatabase();
}


void
DatabaseConnector::ReadCellsStates(double txs[], int noCells)
{
	while(!IsDatabaseUnlocked())
	{
		usleep(100);
	}
	LockDatabase();

	SetCollection("cell_configurations");

	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << bsoncxx::builder::stream::finalize);
	for(auto view : cursor)
	{
		std::string cellName;
		for(int i = 1; i < noCells; i++)
		{
			cellName = "Cell" + i;
			auto id = view["CellID"];
			auto tx = view["TxPower"];
			txs[id.get_int32()] = tx.get_double();
		}
	}
	UnlockDatabase();
}


std::vector<Location>
DatabaseConnector::ReadConnectionLocations(std::vector<uint16_t> cells)
{
	while(!IsDatabaseUnlocked())
	{
		usleep(100);
	}
	LockDatabase();
	std::vector<Location> data;
	SetCollection("main_kpis_log");

	// TODO: Find out how to use or statement in driver!
	for(unsigned int i = 0; i < cells.size(); i++)
	{
		mongocxx::cursor cursor1 = mongoCollection->find(bsoncxx::builder::stream::document{} << "CellID" << cells[i] << bsoncxx::builder::stream::finalize);
		for(auto view : cursor1)
		{
			auto connected = view["CONNECTED"];
			if(connected.get_bool())
			{
				auto x = view["LocationX"];
				auto y = view["LocationY"];
				Location l = Location(x.get_double(), y.get_double());
				data.push_back(l);
			}
		}
	}
	UnlockDatabase();
	return data;
}


std::vector<Location>
DatabaseConnector::ReadHandovers(std::vector<uint16_t> cells)
{
	while(!IsDatabaseUnlocked())
	{
			usleep(100);
	}
	LockDatabase();
	std::vector<Location> data;
	SetCollection("handover_log");

	// TODO: Find out how to use or statement in driver!
	for(unsigned int i = 0; i < cells.size(); i++)
	{
		mongocxx::cursor cursor1 = mongoCollection->find(bsoncxx::builder::stream::document{} << "CellID" << cells[i] << bsoncxx::builder::stream::finalize);
		for(auto view : cursor1)
		{
			auto x = view["LocationX"];
			auto y = view["LocationY"];
			Location l = Location(x.get_int32(), y.get_int32());
			data.push_back(l);
		}
		mongocxx::cursor cursor2 = mongoCollection->find(bsoncxx::builder::stream::document{} << "TargetCellID" << cells[i] << bsoncxx::builder::stream::finalize);
		for(auto view : cursor2)
		{
			auto x = view["LocationX"];
			auto y = view["LocationY"];
			Location l = Location(x.get_int32(), y.get_int32());
			data.push_back(l);
		}
	}
	UnlockDatabase();
	return data;
}

void
DatabaseConnector::SaveCellsStates(double txs[], int noCells)
{
	while(!IsDatabaseUnlocked())
	{
		usleep(100);
	}
	LockDatabase();
	SetCollection("cell_configurations");

	for(int i = 1; i < noCells+1; i++)
	{
		mongoCollection->update_one(bsoncxx::builder::stream::document{} << "CellID" << i << bsoncxx::builder::stream::finalize,
							bsoncxx::builder::stream::document{} << "$set" << bsoncxx::builder::stream::open_document <<
							"TxPower" << txs[i] << bsoncxx::builder::stream::close_document << bsoncxx::builder::stream::finalize);

	}
	UnlockDatabase();
}

std::vector<int>
DatabaseConnector::ReadRLFs(float time, float variance)
{
	while(!IsDatabaseUnlocked())
	{
		usleep(100);
	}
	LockDatabase();
	SetCollection("event_log");
	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << "Time" << bsoncxx::builder::stream::open_document << "$gte" << (time-variance) << bsoncxx::builder::stream::close_document << "EventID" << 0 << bsoncxx::builder::stream::finalize);
	UnlockDatabase();
	std::vector<int> labeledUsers;
	for(auto view : cursor)
	{
		auto ue = view["UserID"];
		labeledUsers.push_back(ue.get_int64());
	}
	return labeledUsers;
}

void
DatabaseConnector::ReadSimulationState(uint32_t& nMacroEnbSites, uint32_t& nMacroEnbSitesX, double& interSiteDistances, int32_t& pid)
{
	while(!IsDatabaseUnlocked())
	{
		usleep(100);
	}
	LockDatabase();
	SetCollection("simulation_configurations");

	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << bsoncxx::builder::stream::finalize);
	for(auto view : cursor)
	{
		auto macro = view["nMacroEnbSites"];
		auto macroX = view["nMacroEnbSitesX"];
		auto interSite = view["interSiteDistance"];
		auto pidDb = view["pid"];

		nMacroEnbSites = (uint32_t)macro.get_int32();
		nMacroEnbSitesX = (uint32_t)macroX.get_int32();
		pid = (int32_t)pidDb.get_int32();
		interSiteDistances = interSite.get_double();
	}
	UnlockDatabase();
}

void
DatabaseConnector::SaveSimulationState(uint32_t nMacroEnbSites, uint32_t nMacroEnbSitesX, double interSiteDistance, int pid)
{
	while(!IsDatabaseUnlocked())
	{
		usleep(100);
	}
	LockDatabase();

	SetDatabase("5gopt");
	SetCollection("simulation_configurations");

	std::vector<bsoncxx::document::value> documents;
	bsoncxx::builder::stream::document doc {};

	doc << "nMacroEnbSites" << (int32_t)nMacroEnbSites << "nMacroEnbSitesX" << (int32_t)nMacroEnbSitesX << "interSiteDistance" << interSiteDistance << "pid" << pid;
	documents.push_back(doc << bsoncxx::builder::stream::finalize);
	mongoCollection->insert_many(documents);
	UnlockDatabase();
}

void
DatabaseConnector::ClearAllLogs()
{
	eventsLog.clear();
	handoversLog.clear();
	sinrsLog.clear();
	throughputsLog.clear();
	mainKpisLog.clear();
	remLog.clear();
	mainKpisWithLabelLog.clear();
	statusLog.clear();
//	eventsLogCol.Clear();
//	handoversLogCol.Clear();
//	sinrsLogCol.Clear();
//	throughputsLogCol.Clear();
//	mainKpisLogCol.Clear();
}

bool
DatabaseConnector::RunMongoStartScript()
{
	// If not already running::
	std::string command = "./run_mongoDB.sh";
	std::string dbpath = "./home/tupevarj/Downloads/mongodb-linux-x86_64-rhel70-3.4.10/bin/data/db";

	command = command + " " + dbpath;
	int success = system(command.c_str());
	if(success == -1)
	{
		std::cout << "Error running script.. " << std::endl;
	}
	return true;
}

DatabaseConnector::~DatabaseConnector()
{
	delete mongoClient;
	delete mongoDatabase;
	delete mongoCollection;

	ClearAllLogs();
}

static int nRounds = 0;

void
DatabaseConnector::RunMatlabKpiScript()
{
	std::ostringstream convert;
	convert << nRounds++;
	std::string command = "./run_matlab_KPI.sh";
//	std::string nexMapName = "\"/home/tupevarj/NS3SimulatorData/kuva" + convert.str() + ".bmp\"";
	std::string nexMapName = "\"/home/tupevarj/NS3SimulatorData/kuva1.bmp\"";

	command = command + " " + nexMapName;
	int success = system(command.c_str());
	if(success == -1)
	{
		std::cout << "Error running script.. " << std::endl;
	}
}

void
DatabaseConnector::RunMatlabRemScript()
{
	static int nImages = 0;
	std::ostringstream convert;
	convert << nImages++;
	std::string command = "./run_matlab_REM.sh";
	std::string nexMapName = "\"/home/tupevarj/NS3SimulatorData/kuva" + convert.str() + ".bmp\"";

	//command = command + " " + nexMapName;
	int success = system(command.c_str());
	if(success == -1)
	{
		std::cout << "Error running script.. " << std::endl;
	}
}


void
DatabaseConnector::dropDatabase()
{
	SetCollection("simulation_configurations");
	mongoCollection->drop();
	SetCollection("cell_configurations");
	mongoCollection->drop();
	SetCollection("controlpanel");
	mongoCollection->drop();
	SetCollection("rem_log");
	mongoCollection->drop();
	SetCollection("event_log");
	mongoCollection->drop();
	SetCollection("handover_log");
	mongoCollection->drop();
	SetCollection("main_kpis_log");
	mongoCollection->drop();
	SetCollection("sinr_log");
	mongoCollection->drop();
	SetCollection("throughput_log");
	mongoCollection->drop();
	SetCollection("locks");
	mongoCollection->drop();
	SetCollection("status_log");
	mongoCollection->drop();
}

void
DatabaseConnector::RunREMGeneratorScript(int stepId)
{
	std::string command = "./run_REM_generator.sh";
	std::ostringstream s;
	s << stepId;
	std::string stepString(s.str());

	command = command + " " + stepString;
	int success = system(command.c_str());
	if(success == -1)
	{
		std::cout << "Error running script.. " << std::endl;
	}
}

void
DatabaseConnector::ClearSimulationState()
{
	SetCollection("simulation_configurations");
	mongoCollection->drop();
//	SetCollection("Ns3StateSettings");


}
