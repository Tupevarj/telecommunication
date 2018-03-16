#include "ConfigureInOut.h"
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

ConfigureInOut::ConfigureInOut() : mongoClient(NULL), mongoDatabase(NULL), mongoCollection(NULL)
{

}

////////////////////////////////////////////////////////////////////////////////////
//	MONGO DB
////////////////////////////////////////////////////////////////////////////////////


/* HUOM!!! Skripti ei toimi vielä: --dbpath ei toimi */
void
ConfigureInOut::CreateConnectionToDataBase()
{
	// RunMongoStartScript();
	mongocxx::instance inst{};
	mongoClient = new mongocxx::client{mongocxx::uri{}};
}


void
ConfigureInOut::SetDatabase(std::string db)
{
	mongoDatabase = new mongocxx::database{mongoClient->database(db)};
	//m_confData = new ConfigurationData();
//	mongocxx::client conn{mongocxx::uri{}};

//	bsoncxx::builder::stream::document document{};



//
//	auto collection = conn["n3_db"]["testcollectionNS3"];
//	document << "hello" << "world";
//
//	collection.insert_one(document.view());
//	auto cursor = collection.find({});
//
//	for (auto&& doc : cursor) {
//	        std::cout << bsoncxx::to_json(doc) << std::endl;
//	}
//	return true;
}

void
ConfigureInOut::SetCollection(std::string coll)
{
	mongoCollection = new mongocxx::collection{mongoDatabase->collection(coll)};
}

void
ConfigureInOut::TestWriteToCurrentCollection()
{
	bsoncxx::builder::stream::document document{};
	document << "name:" << "Tuukka" << "lastName" << "Varjus";

	mongoCollection->insert_one(document.view());
}




void
ConfigureInOut::LogEvent(double time, double x, double y,uint64_t imsi, EventName e, uint16_t cellId, double rsr)
{
	eventsLog.push_back(EventLog{time, x, y, rsr, imsi, cellId, e});
//	eventsLogCol.AddLog(new EventLog{time, x, y, rsr, imsi, cellId, e});
}

void
ConfigureInOut::LogHandover(double time, double x, double y,uint64_t imsi, HandoverEventName e, uint16_t cellId, uint16_t targetCellId)
{
	handoversLog.push_back(HandoverLog{time, x, y, imsi, cellId, targetCellId, e});
	//handoversLogCol.AddLog(new HandoverLog{time, x, y, imsi, cellId, targetCellId, e});
}

void
ConfigureInOut::LogSinr(double time, uint64_t imsi, uint16_t cellId, double sinr)
{
	//sinrsLogCol.AddLog(new SinrLog{time, sinr, imsi, cellId});
	sinrsLog.push_back(SinrLog{time, sinr, imsi, cellId});
}

void
ConfigureInOut::LogThroughput(double time, uint64_t imsi, uint16_t cellId, double thr)
{
//	throughputsLogCol.AddLog(new ThrouhgputLog{time, thr, imsi, cellId});
	throughputsLog.push_back(ThrouhgputLog{time, thr, imsi, cellId});
}

void
ConfigureInOut::LogMainKpisWithLabeling(double time, double x, double y, uint64_t imsi, uint16_t cellId, double rsrp, double rsrq, bool connected, bool label)
{
	mainKpisWithLabelLog.push_back(MainKpiWithLabelLog{time, x, y, rsrp, rsrq, imsi, cellId, connected, label});
}

void
ConfigureInOut::LogMainKpis(double time, double x, double y, uint64_t imsi, uint16_t cellId, double rsrp, double rsrq, bool connected)
{
//	mainKpisLogCol.AddLog(new MainKpiLog{time, x, y, rsrp, rsrq, imsi, cellId});
	mainKpisLog.push_back(MainKpiLog{time, x, y, rsrp, rsrq, imsi, cellId, connected});
}

void
ConfigureInOut::LogREM(double x, double y, double z, double sinr)
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
ConfigureInOut::WriteAllLogsToCSVFiles(std::string prefix)
{
//	WriteLogToCSVFile(prefix + EventLog::FILE_NAME, eventsLogCol);
//	WriteLogToCSVFile(prefix + HandoverLog::FILE_NAME, handoversLogCol);
//	WriteLogToCSVFile(prefix + SinrLog::FILE_NAME, sinrsLogCol);
//	WriteLogToCSVFile(prefix + ThrouhgputLog::FILE_NAME, throughputsLogCol);
//	WriteLogToCSVFile(prefix + MainKpiLog::FILE_NAME, mainKpisLogCol);
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
ConfigureInOut::WriteLogsToDatabase()
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
		SetCollection("main_kpis_log_labels");

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
		SetCollection("dominationmap");

		for(uint i = 0; i < remLog.size(); ++i)
		{
			documents.push_back(remLog[i].ConvertToBSON() << bsoncxx::builder::stream::finalize);
		}
		mongoCollection->insert_many(documents);
		documents.clear();
	}
}

SONEngineLog
ConfigureInOut::ReadSONEngineMethodsFromDatabase()
{
	while(!IsDatabaseUnlocked(true))
	{
		usleep(100);
	}
	LockDatabase(true);
	SetCollection("controlpanel");
	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << "outage" << 1 << "dirty_flag" << 0 << bsoncxx::builder::stream::finalize);


	SONEngineLog configuration =  SONEngineLog(cursor);

	/* UPDATE DIRTY FLAGS */
	bsoncxx::stdx::optional<mongocxx::result::update> result =
			mongoCollection->update_many(bsoncxx::builder::stream::document{} << "dirty_flag" << 0 << bsoncxx::builder::stream::finalize,
					bsoncxx::builder::stream::document{} << "$set" << bsoncxx::builder::stream::open_document << "dirty_flag" << 1 <<
					bsoncxx::builder::stream::close_document << bsoncxx::builder::stream::finalize);
	UnlockDatabase(true);


	return configuration;
//	}
}

/* todo: Check connection to database! SIGSEGV Error jos MongoDB ei ole käynnissä!!!!!!!!!!!!!! */
ConfigurationLog
ConfigureInOut::ReadConfigurationFromDatabase()
{
	while(!IsDatabaseUnlocked(true))
	{
		usleep(100);
	}
	LockDatabase(true);
	//int confNo = 0;// todo: GetConfigurationNumber() ++
//
	SetDatabase("CellConfigurations");
	SetCollection("TxPowers");
//
//	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << "Step" << confNo << bsoncxx::builder::stream::finalize);

	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << bsoncxx::builder::stream::finalize);
	ConfigurationLog configuration =  ConfigurationLog(cursor);
	UnlockDatabase(true);
	//TODO: SET LAST DATABASE
	SetDatabase("5gopt");
	return configuration;
}


void
ConfigureInOut::UpdateTxPower(u_int16_t cellId, double tx)
{
	while(!IsDatabaseUnlocked(false))
	{
		usleep(100);
	}
	LockDatabase(false);
	SetDatabase("CellConfigurations");
	SetCollection("TxPowers");
	// Update
	mongoCollection->update_one(bsoncxx::builder::stream::document{} << "CellID" << cellId << bsoncxx::builder::stream::finalize,
				bsoncxx::builder::stream::document{} << "$set" << bsoncxx::builder::stream::open_document <<
				"TxPower" << tx << bsoncxx::builder::stream::close_document << bsoncxx::builder::stream::finalize);

	UnlockDatabase(false);
	SetDatabase("5gopt");
}

bool
ConfigureInOut::CheckConnectionToDatabase()
{
	// todo: Check connection, relevant?
	return true;
}


void
ConfigureInOut::SetOutPutFolder(std::string path)
{
	outputFolder = path;
}


bool
ConfigureInOut::IsDatabaseUnlocked(bool read)
{
	SetDatabase("5gopt"); // TODO: use differenttrue db?
	SetCollection("Locks");
	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << bsoncxx::builder::stream::finalize);
	int count = 0;
	for(auto view : cursor)
	{
		count++;
		auto type = view["Type"];
	//	auto timeStamp = view["Time"];   // TODO: maybe use timestamp to find if lock is created long time a ago

	//	time_t time = std::time(0);
		int t = type.get_int32();

		//  && (timeStamp + 1) < time
		if(t == 0) return true;
		if(read && t > 0) return true;
	}
	if(count == 0) return true;
	return false;
}

void
ConfigureInOut::LockDatabase(bool read)
{
	SetDatabase("5gopt"); // TODO: use different db?
	SetCollection("Locks");

	//int type = 1;
	//if(!read) type = -1;

	time_t time = std::time(0);

	mongocxx::options::update options;
    options.upsert(true);

	if(read)
	{
		mongoCollection->update_one(bsoncxx::builder::stream::document{} << bsoncxx::builder::stream::finalize,
		bsoncxx::builder::stream::document{} << "$inc" << bsoncxx::builder::stream::open_document << "Type" << 1 << "Time" << time <<
		bsoncxx::builder::stream::close_document << bsoncxx::builder::stream::finalize, options);
	}
	else
	{
		mongoCollection->update_one(bsoncxx::builder::stream::document{} << bsoncxx::builder::stream::finalize,
		bsoncxx::builder::stream::document{} << "$set" << bsoncxx::builder::stream::open_document << "Type" << -1 << "Time" << time <<
		bsoncxx::builder::stream::close_document << bsoncxx::builder::stream::finalize, options);
	}
	// TODO: Check correctness of find()!
}


void
ConfigureInOut::UnlockDatabase(bool read)
{
	SetDatabase("5gopt"); // TODO: use different db?
	SetCollection("Locks");

	if(read)
	{
		mongoCollection->update_one(bsoncxx::builder::stream::document{} << bsoncxx::builder::stream::finalize,
		bsoncxx::builder::stream::document{} << "$inc" << bsoncxx::builder::stream::open_document << "Type" << -1 <<
		bsoncxx::builder::stream::close_document << bsoncxx::builder::stream::finalize);
	}
	else
	{
		mongoCollection->update_one(bsoncxx::builder::stream::document{} << bsoncxx::builder::stream::finalize,
		bsoncxx::builder::stream::document{} << "$set" << bsoncxx::builder::stream::open_document << "Type" << 0 <<
		bsoncxx::builder::stream::close_document << bsoncxx::builder::stream::finalize);
	}
}

void
ConfigureInOut::FlushLogs()
{
	if(mongoClient)
	{
		// TODO:
		while(!IsDatabaseUnlocked(false))
		{
			usleep(10000);
		}
		LockDatabase(false);
		WriteLogsToDatabase();
		//	WriteAllLogsToCSVFiles(outputFolder); // <- DEBUG
		ClearAllLogs();
		UnlockDatabase(false);
	}
	else
	{
		WriteAllLogsToCSVFiles(outputFolder);
		ClearAllLogs();
	}
}


void
ConfigureInOut::SetPostFixCSV(std::string postFix)
{
	this->postFix = postFix;
}

void
ConfigureInOut::InitializeCellConfigurations(double txPower, int noCells)
{
	while(!IsDatabaseUnlocked(false))
	{
		usleep(100);
	}
	LockDatabase(false);

	SetDatabase("CellConfigurations");
	SetCollection("TxPowers");
	mongoCollection->drop();

	std::vector<bsoncxx::document::value> documents;

	for(int i = 1; i <= noCells; i++)
	{
		bsoncxx::builder::stream::document doc {};
		doc << "CellID" << i << "TxPower" << txPower;
		documents.push_back(doc << bsoncxx::builder::stream::finalize);
	}
	mongoCollection->insert_many(documents);
	UnlockDatabase(false);
}


void
ConfigureInOut::ReadCellsStates(double txs[], int noCells,  int stepId)
{
	while(!IsDatabaseUnlocked(true))
	{
		usleep(100);
	}
	LockDatabase(true);

	SetCollection("Ns3TransmissionPowers");

	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << "Step" << stepId << bsoncxx::builder::stream::finalize);
	for(auto view : cursor)
	{
		std::string cellName;
		for(int i = 1; i < noCells; i++)
		{
			cellName = "Cell" + i;
			auto id = view["CellId"];
			auto tx = view["TxPower"];
			txs[id.get_int32()] = tx.get_double();
		}
	}
	UnlockDatabase(true);
}


std::vector<Location>
ConfigureInOut::ReadHandovers(std::vector<uint16_t> cells)
{
	while(!IsDatabaseUnlocked(true))
	{
			usleep(100);
	}
	LockDatabase(true);
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
	UnlockDatabase(true);
	return data;
}

void
ConfigureInOut::SaveCellsStates(double txs[], int noCells, int stepId)
{
	while(!IsDatabaseUnlocked(false))
	{
		usleep(100);
	}
	LockDatabase(false);
	SetCollection("Ns3TransmissionPowers");
	std::vector<bsoncxx::document::value> documents;

	for(int i = 1; i < noCells+1; i++)
	{
		bsoncxx::builder::stream::document doc {};
		doc << "CellId" << i << "TxPower" << txs[i] << "Step" << stepId;
		documents.push_back(doc << bsoncxx::builder::stream::finalize);
	}
	mongoCollection->insert_many(documents);
	UnlockDatabase(false);
}


void
ConfigureInOut::ReadSimulationState(uint32_t& nMacroEnbSites, uint32_t& nMacroEnbSitesX, double& interSiteDistances, int32_t& pid)
{
	while(!IsDatabaseUnlocked(true))
	{
		usleep(100);
	}
	LockDatabase(true);
	SetCollection("Ns3StateSettings");

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
	UnlockDatabase(true);
}

void
ConfigureInOut::SaveSimulationState(uint32_t nMacroEnbSites, uint32_t nMacroEnbSitesX, double interSiteDistance, int pid)
{
	while(!IsDatabaseUnlocked(false))
	{
		usleep(100);
	}
	LockDatabase(false);

	SetDatabase("5gopt");
	SetCollection("Ns3StateSettings");

	std::vector<bsoncxx::document::value> documents;
	bsoncxx::builder::stream::document doc {};

	doc << "nMacroEnbSites" << (int32_t)nMacroEnbSites << "nMacroEnbSitesX" << (int32_t)nMacroEnbSitesX << "interSiteDistance" << interSiteDistance << "pid" << pid;
	documents.push_back(doc << bsoncxx::builder::stream::finalize);
	mongoCollection->insert_many(documents);
	UnlockDatabase(false);
}

void
ConfigureInOut::ClearAllLogs()
{
	eventsLog.clear();
	handoversLog.clear();
	sinrsLog.clear();
	throughputsLog.clear();
	mainKpisLog.clear();
	remLog.clear();
	mainKpisWithLabelLog.clear();
//	eventsLogCol.Clear();
//	handoversLogCol.Clear();
//	sinrsLogCol.Clear();
//	throughputsLogCol.Clear();
//	mainKpisLogCol.Clear();
}

bool
ConfigureInOut::RunMongoStartScript()
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

ConfigureInOut::~ConfigureInOut()
{
	delete mongoClient;
	delete mongoDatabase;
	delete mongoCollection;

	ClearAllLogs();
}

static int nRounds = 0;

void
ConfigureInOut::RunMatlabKpiScript()
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
ConfigureInOut::RunMatlabRemScript()
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
ConfigureInOut::dropDatabase()
{
	mongoDatabase->drop();
}

void
ConfigureInOut::RunREMGeneratorScript(int stepId)
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
ConfigureInOut::ClearSimulationState()
{
	SetCollection("Ns3StateSettings");
	mongoCollection->drop();
//	SetCollection("Ns3StateSettings");


}
