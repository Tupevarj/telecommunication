/*
 * ConfigureInOutStructures.h
 *
 *  Created on: 12.12.2017
 *      Author: tupevarj
 *
 */
#pragma once
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <bsoncxx/builder/stream/document.hpp>
#include <bsoncxx/document/value.hpp>
#include <bsoncxx/document/element.hpp>
#include <mongocxx/cursor.hpp>
#include <cstdlib>



struct Location
{
	double x;
	double y;

	Location(double x, double y) : x(x), y(y) {};
};


////////////////////////////////////////////////////////////////////////////////////
//	CONFIGURATION FOR SINGLE CELL
////////////////////////////////////////////////////////////////////////////////////

struct CellConfiguration
{
	u_int16_t cellId;
	double txPower;
	// possible antenna tilt and other settings..

	CellConfiguration(int id, double power) : cellId(id), txPower(power) {};
};


////////////////////////////////////////////////////////////////////////////////////
//	SON ENGINE CONFIGURATIONS
////////////////////////////////////////////////////////////////////////////////////



struct SONEngineConfiguration
{
	enum SonEngineMethod
	{
		Normal,
		Outage,
		COC,
		CCO,
		MRO,
		MLB
	};

	SonEngineMethod method;
	u_int16_t cellId;

	// possible antenna tilt and other settings..

	SONEngineConfiguration(u_int16_t id, SonEngineMethod method) : method(method), cellId(id) {};
};

////////////////////////////////////////////////////////////////////////////////////
//	ENUMERATION FOR EVENTS
////////////////////////////////////////////////////////////////////////////////////

/* Event name enum  1,2,3,6 */
enum EventName
{
	RLF,
	OutOfSynch,
	A3RSRPEnter,
	A2RSRQLeave,
	A2RSRPLeave,
	A2RSRPEnter,
	A2RSRQEnter
};

/* Handover name enum */
enum HandoverEventName
{
	HandoverStart,
	HandoverEndOK
};

////////////////////////////////////////////////////////////////////////////////////
//	SIMULATION OUTPUT STRUCTURES
////////////////////////////////////////////////////////////////////////////////////

/*
 * Base output file structure.
 *
 */
struct WritableLog
{
	virtual std::string ConvertToCSV() = 0;
	virtual bsoncxx::builder::stream::document ConvertToBSON() = 0;
//	virtual std::string GetFileName() = 0;

protected:
	virtual ~WritableLog() {};
};



struct REMLog : public WritableLog
{
	///////////////////////////////////
	// MEMBERS
	///////////////////////////////////

	double x;
	double y;
	double z;
	double sinr;

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	REMLog(double x, double y, double z, double sinr) : x(x), y(y), z(z), sinr(sinr)
	{

	}

	inline
	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << x << "," << y << "," << z << "," << sinr;
		return strs.str();
	}

	inline
	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
		doc << "x" << x << "y" << y << "z" << z << "sinr" << sinr;
		return doc;
	}

	static std::string GetFileName()
	{
		return "rem_log";
	}
};

/*
 *  Output file structure for events:
 *  - time
 *  - x position
 *  - y position
 *  - imsi
 *  - cell ID
 *  - Handover Event (int)
 *  - RSRP or RSRQ (depends on event!)
 */
struct EventLog : public WritableLog
{
	///////////////////////////////////
	// MEMBERS
	///////////////////////////////////

	double time;
	int x;
	int y;
	double rsr;
	uint64_t imsi;
	uint16_t cellId;
	EventName e;

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	EventLog(double time, double x, double y, double rsr, uint64_t imsi, uint16_t cellId, EventName e)
		: time(time), x(x), y(y), rsr(rsr), imsi(imsi), cellId(cellId), e(e)
	{

	}

	inline
	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << time << "," << x << "," << y << "," << imsi << "," << e << "," << cellId << "," << rsr;
		return strs.str();
	}

	inline
	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
		doc << "Time" << time << "LocationX" << x << "LocationY" << y << "UserID" << (int64_t)imsi
			<< "EventID" << e << "CellID" << (int16_t)cellId << "RSRQ" << rsr;
		return doc;
	}

	static std::string GetFileName()
	{
		return "event_log";
	}
};

/*
 *  Output file structure for handovers:
 *  - time
 *  - x position
 *  - y position
 *  - imsi
 *  - cell ID
 *  - Handover Event (int)
 *  - Target Cell ID (optional)
 */
struct HandoverLog : public WritableLog
{
	///////////////////////////////////
	// MEMBERS
	///////////////////////////////////

	double time;
	int x;
	int y;
	uint64_t imsi;
	uint16_t cellId;
	uint16_t targetCellId;
	HandoverEventName e;

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	HandoverLog(double time, double x, double y, uint64_t imsi, uint16_t cellId, uint16_t targetCellId, HandoverEventName e)
			: time(time), x(x), y(y), imsi(imsi), cellId(cellId), targetCellId(targetCellId), e(e)
	{

	}

	inline
	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << time << "," << x << "," << y << "," << imsi << "," << e << "," << cellId << "," << targetCellId;
		return strs.str();
	}

	inline
	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
		doc << "Time" << time << "LocationX" << x << "LocationY" << y << "UserID" << (int64_t)imsi
			<< "HEventID" << e << "CellID" << (int16_t)cellId << "TargetCellID"
			<< (int16_t)targetCellId;
		return doc;
	}
	static std::string GetFileName()
	{
		return "handover_log";
	}
};


/*
 *  Output file structure for handovers:
 *  - time
 *  - x position
 *  - y position
 *  - imsi
 *  - cell ID
 *  - Handover Event (int)
 *  - Target Cell ID (optional)
 */
struct StatusLog : public WritableLog
{
	///////////////////////////////////
	// MEMBERS
	///////////////////////////////////

	std::string time;
	std::string message;
	int type;

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	StatusLog(std::string time, std::string message, int type) : time(time), message(message), type(type)
	{

	}

	inline
	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << time << "," << message << type;
		return strs.str();
	}

	inline
	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
					doc << "Time" << time << "Message" << message << "Type" << type;
		return doc;
	}
	static std::string GetFileName()
	{
		return "status_log";
	}
};

/*
 *  Output file structure for SINR:
 *  - time
 *  - imsi
 *  - cell ID
 *  - SINR
 */
struct SinrLog : public WritableLog
{
	///////////////////////////////////
	// MEMBERS
	///////////////////////////////////

	double time;
	double sinr;
	uint64_t imsi;
	uint16_t cellId;

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	SinrLog(double time, double sinr, uint64_t imsi, uint16_t cellId)
			: time(time), sinr(sinr), imsi(imsi), cellId(cellId)
	{

	}

	inline
	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << time << "," << imsi << "," << cellId << "," << sinr;
		return strs.str();
	}

	inline
	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
		doc << "Time" << time << "UserID" << (int64_t)imsi << "CellID" << (int16_t)cellId
			<< "SINR" << sinr;
		return doc;
	}

	static std::string GetFileName()
	{
		return "sinr_log";
	}
};

/*
 *  Output file structure for throuhgput:
 *  - time
 *  - imsi
 *  - cell ID
 *  - throughput
 */
struct ThrouhgputLog : public WritableLog
{
	///////////////////////////////////
	// MEMBERS
	///////////////////////////////////

	double time;
	double throughput;
	uint64_t imsi;
	uint16_t cellId;

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	ThrouhgputLog(double time, double throughput, uint64_t imsi, uint16_t cellId)
				: time(time), throughput(throughput), imsi(imsi), cellId(cellId)
	{

	}

	inline
	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << time << "," << imsi << "," << cellId << "," << throughput;
		return strs.str();
	}

	inline
	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
		doc << "Time" << time << "UserID" << (int64_t)imsi << "CellID" << (int16_t)cellId
			<< "Throughput" << throughput;
		return doc;
	}

	static std::string GetFileName()
	{
		return "throughput_log";
	}
};


/*
 *  Output file structure foe main KPIs:
 *  - time
 *  - x position
 *  - y position
 *  - imsi
 *  - cell ID
 *  - RSRP
 *  - RSRQ
 */
struct MainKpiLog : public WritableLog
{
	///////////////////////////////////
	// MEMBERS
	///////////////////////////////////

	double time;
	double x;
	double y;
	double rsrp;
	double rsrq;
	uint64_t imsi;
	uint16_t cellId;
	bool connected;

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	MainKpiLog(double time, double x, double y, double rsrp, double rsrq, uint64_t imsi, uint16_t cellId, bool connected)
			: time(time), x(x), y(y), rsrp(rsrp), rsrq(rsrq), imsi(imsi), cellId(cellId), connected(connected)
	{

	}

	inline
	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << time << "," << x << "," << y << "," << imsi << "," << cellId << "," << rsrp << "," << rsrq << "," << connected;
		return strs.str();
	}

	inline
	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
		doc << "Time" << time << "LocationX" << x << "LocationY" << y << "UserID" << (int64_t)imsi
			<< "CellID" << (int16_t)cellId << "RSRP" << rsrp << "RSRQ" << rsrq << "CONNECTED" << connected;
		return doc;
	}


	/* Fake data for throughput graph */
//	bsoncxx::builder::stream::document ConvertToBSON() override
//	{
//
//		int randomNumber = std::rand() % 100;
//
//		bsoncxx::builder::stream::document doc {};
//		doc << "Time" << time << "UserThR" << randomNumber << "LocationX" << x << "UserID" << (int)imsi
//			<< "CellID" << (int16_t)cellId << "RSRP" << rsrp << "RSRQ" << rsrq << "SINR" << randomNumber << "LocationY" << y;
//		return doc;
//	}


	static std::string GetFileName()
	{
		return "main_log";
	}
};

/*
 * 	Main KPIs log for training
 *
 */
struct MainKpiWithLabelLog : public MainKpiLog
{
	bool label;

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	MainKpiWithLabelLog(double time, double x, double y, double rsrp, double rsrq, uint64_t imsi, uint16_t cellId, bool connected, bool label)
				: MainKpiLog(time, x, y, rsrp, rsrq, imsi, cellId, connected), label(label)
	{

	}

	inline
	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << time << "," << x << "," << y << "," << imsi << "," << cellId << "," << rsrp << "," << rsrq << "," << connected << "," << label;
		return strs.str();
	}

	inline
	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
		doc << "Time" << time << "LocationX" << x << "LocationY" << y << "UserID" << (int64_t)imsi
			<< "CellID" << (int16_t)cellId << "RSRP" << rsrp << "RSRQ" << rsrq << "CONNECTED" << connected << "LABEL" << (uint16_t)label;
			return doc;
	}
	static std::string GetFileName()
	{
		return "main_log_with_labels";
	}
};

/*
 * Input configuration file structure
 */
struct ConfigurationLog
{
	///////////////////////////////////
	// MEMBERS
	///////////////////////////////////

	std::vector<CellConfiguration> configurations;

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	ConfigurationLog()
	{

	}


	ConfigurationLog(mongocxx::cursor& cursor)
	{
		for(auto view : cursor)
		{
			auto cellId = view["CellID"];
			auto txp = view["TxPower"];
			configurations.push_back(CellConfiguration(cellId.get_int32(), txp.get_double()));
		}
	}

	void
	Clone(ConfigurationLog log)
	{
		configurations.clear();
		for(unsigned int i = 0; i < log.configurations.size(); i++)
		{
			configurations.push_back(log.configurations[i]);
		}

	}
};

/*
 * Input configuration file structure
 */
struct SONEngineLog
{
	///////////////////////////////////
	// MEMBERS
	///////////////////////////////////

	std::vector<SONEngineConfiguration> configurations;

	static
	std::string GetMethodName(int i)
	{
		switch(i)
		{
			case 0 : return "Normal";
			break;
			case 1 : return "Outage";
			break;
			case 2 : return "COC";
			break;
			case 3 : return "CCO";
			break;
			case 4 : return "MRO";
			break;
			case 5 : return "MLB";
			break;
		}
		return "Not correct method number";
	};

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	// EI KOVIN FIKSU TOTEUTUS: TIETOKANNASSA PITÄISI OLLA AINOASTAAN YKSI NUMERO TALLENNETTUNA, JOKA KERTOO
	// METHODIN, KOSKA VAIN YKSI METODI VOI OLLA KÄYTÖSSÄ!! todo: keskustele Yi:n kanssa.
	SONEngineLog(mongocxx::cursor& cursor)
	{
		for(auto view : cursor)
		{
			auto cellId = view["cellID"];

			bsoncxx::document::element element = view["normal"];


			if(element.type() == bsoncxx::type::k_double)
			{

				///////////////////////////////////
				// IF DOUBLE
				///////////////////////////////////

				auto method = view["normal"];
				if(method.get_double() == 1)
				{
					configurations.push_back(SONEngineConfiguration(cellId.get_double(), SONEngineConfiguration::SonEngineMethod::Normal));
					continue;
				}
				method = view["outage"];
				if(method.get_double() == 1)
				{
					configurations.push_back(SONEngineConfiguration(cellId.get_double(), SONEngineConfiguration::SonEngineMethod::Outage));
					continue;
				}
				method = view["coc"];
				if(method.get_double() == 1)
				{
					configurations.push_back(SONEngineConfiguration(cellId.get_double(), SONEngineConfiguration::SonEngineMethod::COC));
					continue;
				}
				method = view["cco"];
				if(method.get_double() == 1)
				{
					configurations.push_back(SONEngineConfiguration(cellId.get_double(), SONEngineConfiguration::SonEngineMethod::CCO));
					continue;
				}
				method = view["mro"];
				if(method.get_double() == 1)
				{
					configurations.push_back(SONEngineConfiguration(cellId.get_double(), SONEngineConfiguration::SonEngineMethod::MRO));
					continue;
				}
				method = view["mlb"];
				if(method.get_double() == 1)
				{
					configurations.push_back(SONEngineConfiguration(cellId.get_double(), SONEngineConfiguration::SonEngineMethod::MLB));
					continue;
				}
			}


			else if(element.type() == bsoncxx::type::k_int32)
			{
				///////////////////////////////////
				// IF INTEGER
				///////////////////////////////////

				auto method = view["normal"];
				if(method.get_int32() == 1)
				{
					configurations.push_back(SONEngineConfiguration(cellId.get_int32(), SONEngineConfiguration::SonEngineMethod::Normal));
					continue;
				}
				method = view["outage"];
				if(method.get_int32() == 1)
				{
					configurations.push_back(SONEngineConfiguration(cellId.get_int32(), SONEngineConfiguration::SonEngineMethod::Outage));
					continue;
				}
				method = view["coc"];
				if(method.get_int32() == 1)
				{
					configurations.push_back(SONEngineConfiguration(cellId.get_int32(), SONEngineConfiguration::SonEngineMethod::COC));
					continue;
				}
				method = view["cco"];
				if(method.get_int32() == 1)
				{
					configurations.push_back(SONEngineConfiguration(cellId.get_int32(), SONEngineConfiguration::SonEngineMethod::CCO));
					continue;
				}
				method = view["mro"];
				if(method.get_int32() == 1)
				{
					configurations.push_back(SONEngineConfiguration(cellId.get_int32(), SONEngineConfiguration::SonEngineMethod::MRO));
					continue;
				}
				method = view["mlb"];
				if(method.get_int32() == 1)
				{
					configurations.push_back(SONEngineConfiguration(cellId.get_int32(), SONEngineConfiguration::SonEngineMethod::MLB));
					continue;
				}
			}
		}
	}
};

struct LogCollection
{
	std::vector<WritableLog*> logs;

//	template<class T>
//	LogCollection(std::vector<T> v) : logs(v.begin(), v.end())
//	{
//
//	}
//
//
//	~LogCollection()
//	{
//		Clear();
//	}
//
//	/* Ei välttämätön */
//	void AddLog(WritableLog* log)
//	{
//		logs.push_back(log);
//	}
//
//	void Clear()
//	{
//		for (std::vector< WritableLog* >::iterator it = logs.begin() ; it != logs.end(); ++it)
//		{
//			delete (*it);
//		}
//		logs.clear();
//	}
};


////////////////////////////////////////////////////////////////////////////////////
