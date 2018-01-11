#include "ConfigureInOut.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <ios>
#include <cstdlib>

#include <mongocxx/cursor.hpp>

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
ConfigureInOut::LogMainKpis(double time, double x, double y, uint64_t imsi, uint16_t cellId, double rsrp, double rsrq)
{
//	mainKpisLogCol.AddLog(new MainKpiLog{time, x, y, rsrp, rsrq, imsi, cellId});
	mainKpisLog.push_back(MainKpiLog{time, x, y, rsrp, rsrq, imsi, cellId});
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
		outFile.open((prefix + EventLog::GetFileName()).c_str(), std::ios_base::app);
		for(uint i = 0; i < eventsLog.size(); ++i)
		{
			outFile	<< eventsLog[i].ConvertToCSV() << "\n";
		}
		outFile.close();
	}
	if(handoversLog.size() > 0)
	{
		std::ofstream outFile;
		outFile.open((prefix + HandoverLog::GetFileName()).c_str(), std::ios_base::app);
		for(uint i = 0; i < handoversLog.size(); ++i)
		{
			outFile	<< handoversLog[i].ConvertToCSV() << "\n";
		}
		outFile.close();
	}
	if(sinrsLog.size() > 0)
	{
		std::ofstream outFile;
		outFile.open((prefix + SinrLog::GetFileName()).c_str(), std::ios_base::app);
		for(uint i = 0; i < sinrsLog.size(); ++i)
		{
			outFile	<< sinrsLog[i].ConvertToCSV() << "\n";
		}
		outFile.close();
	}
	if(throughputsLog.size() > 0)
	{
		std::ofstream outFile;
		outFile.open((prefix + ThrouhgputLog::GetFileName()).c_str(), std::ios_base::app);
		for(uint i = 0; i < throughputsLog.size(); ++i)
		{
			outFile	<< throughputsLog[i].ConvertToCSV() << "\n";
		}
		outFile.close();
	}
	if(mainKpisLog.size() > 0)
	{
			std::ofstream outFile;
			outFile.open((prefix + MainKpiLog::GetFileName()).c_str(), std::ios_base::app);
			for(uint i = 0; i < mainKpisLog.size(); ++i)
			{
				outFile	<< mainKpisLog[i].ConvertToCSV() << "\n";
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
		SetCollection("TUUKKA_event_log");

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
		SetCollection("TUUKKA_handover_log");

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
		SetCollection("TUUKKA_sinr_log");

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
		SetCollection("TUUKKA_throughputs");

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
		SetCollection("main_file_with_UserTHR");

		for(uint i = 0; i < mainKpisLog.size(); ++i)
		{
			documents.push_back(mainKpisLog[i].ConvertToBSON() << bsoncxx::builder::stream::finalize);
		}
		mongoCollection->insert_many(documents);
		documents.clear();
	}
}

/* todo: Check connection to database! SIGSEGV Error jos MongoDB ei ole käynnissä!!!!!!!!!!!!!! */
ConfigurationLog
ConfigureInOut::ReadConfigurationFromDatabase()
{
	int confNo = 0;// todo: GetConfigurationNumber() ++
//
	SetCollection("configuration");

	mongocxx::cursor cursor = mongoCollection->find(bsoncxx::builder::stream::document{} << "Step" << confNo << bsoncxx::builder::stream::finalize);

	ConfigurationLog configuration =  ConfigurationLog(cursor);
	return configuration;
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

void
ConfigureInOut::FlushLogs()
{
	if(mongoClient)
	{
		// ei ehkä tarpeellista:
		if(CheckConnectionToDatabase())
		{
			WriteLogsToDatabase();
			ClearAllLogs();
		}
		else
		{
			// todo: virheilmoitus, re-try..
		}
	}
	else
	{
		WriteAllLogsToCSVFiles(outputFolder);
		ClearAllLogs();
	}
}

void
ConfigureInOut::ClearAllLogs()
{
	eventsLog.clear();
	handoversLog.clear();
	sinrsLog.clear();
	throughputsLog.clear();
	mainKpisLog.clear();
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
	system(command.c_str());
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
	system(command.c_str());
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
	system(command.c_str());
}
