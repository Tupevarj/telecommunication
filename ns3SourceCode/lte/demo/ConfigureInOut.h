#include <string>
#include <vector>
#pragma once

#include <bsoncxx/builder/stream/document.hpp>
#include <bsoncxx/json.hpp>
#include <bsoncxx/document/value.hpp>
#include <bsoncxx/document/element.hpp>

#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>
#include "ConfigureInOutStructures.h"

// ConfigureInOut class:
// Communicates with mongoDB
//
// todo: level of abstarction
//	- no need to know about ns-3 => boost library
//		log structs:
 //		------------
//		+ log structs 'loopable'
//		+ different location
//		todo: USE INHERITANCE IN WRITING!! (boost?)
//
class ConfigureInOut
{
public:

	ConfigureInOut();
	~ConfigureInOut();

	/* Sets output folder for CSV files */
	void SetOutPutFolder(std::string path);

	/* Runs matlab script for KPIs */
	void RunMatlabKpiScript();

	/* Runs matlab script for REM map */
	void RunMatlabRemScript();

	/* Start using mongodbdatabase instead of writing to files */
	void CreateConnectionToDataBase();

	/* Sets current mongo database */
	void SetDatabase(std::string db);					// todo: make private!??

	void TestWriteToCurrentCollection();

	/* Adds event to cache */
	void LogEvent(double time, double x, double y,uint64_t imsi, EventName e, uint16_t cellId, double rsr);

	/* Adds handover event to cache */
	void LogHandover(double time, double x, double y,uint64_t imsi, HandoverEventName e, uint16_t cellId, uint16_t targetCellId);

	/* Adds SINR values to cache */
	void LogSinr(double time, uint64_t imsi, uint16_t cellId, double sinr);

	/* Add Throuhgput calculations to cache */
	void LogThroughput(double time, uint64_t imsi, uint16_t cellId, double thr);

	/* Adds environment measure to cache */
	void LogMainKpis(double time, double x, double y, uint64_t imsi, uint16_t cellId, double rsrp, double rsrq);

	/* Writes all the logs into database/csv files and CLEARS LOG FILES */
	void FlushLogs();

	/* Reads configuration from database */
	ConfigurationLog ReadConfigurationFromDatabase();

	/* Returns current configuration settings */
	const ConfigurationLog& GetConfigurationData();

private:

	/* Sets current mongo collection in database */
	void SetCollection(std::string coll);

	/*  List of attributes */
//	ConfigurationData m_confData;

	/* Write all logs to CSV files on local disk */
	void WriteAllLogsToCSVFiles(std::string prefix);

	/* Checks connection to databse todo: implement, tarvitaanko? */
	bool CheckConnectionToDatabase();

	/* Saves all the logs to mongoDB */
	void WriteLogsToDatabase();

	/* Clears all the logs */
	void ClearAllLogs();

	/* Starts mongoDB server if not already running */
	bool RunMongoStartScript();

	/* mongoDb client */
	mongocxx::client* mongoClient;
	mongocxx::database* mongoDatabase;
	mongocxx::collection* mongoCollection;

	std::string outputFolder = "/home/tupevarj/NS3SimulatorData/";

//	LogCollection eventsLogCol = {std::vector<WritableLog> {}};
//	LogCollection handoversLogCol = {std::vector<WritableLog> {}};
//	LogCollection sinrsLogCol = {std::vector<WritableLog> {}};
//	LogCollection throughputsLogCol = {std::vector<WritableLog> {}};
//	LogCollection mainKpisLogCol = {std::vector<WritableLog> {}};

	std::vector<EventLog> eventsLog;
	std::vector<HandoverLog> handoversLog;
	std::vector<SinrLog> sinrsLog;
	std::vector<ThrouhgputLog> throughputsLog;
	std::vector<MainKpiLog> mainKpisLog;
};
