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


enum SonEngineMethod
{
	Normal,
	Outage,
	COC,
	CCO,
	MRO,
	MLB
};


struct SONEngineConfiguration
{
	SonEngineMethod method;
	u_int16_t cellId;

	// possible antenna tilt and other settings..

	SONEngineConfiguration(u_int16_t id, SonEngineMethod method) : method(method), cellId(id) {};
};

////////////////////////////////////////////////////////////////////////////////////
//	ENUMERATION FOR EVENTS
////////////////////////////////////////////////////////////////////////////////////

/* Event name enum */
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

	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << x << "," << y << "," << z << "," << sinr;
		return strs.str();
	}

	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
		doc << "x" << x << "y" << y << "z" << z << "sinr" << sinr;
		return doc;
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
	double x;
	double y;
	double rsr;
	uint64_t imsi;
	uint16_t cellId;
	EventName e;

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	EventLog(double time, double x, double y, double rsr, uint64_t imsi, uint16_t cellId, EventName e)
		: time(time), x(x), y(x), rsr(rsr), imsi(imsi), cellId(cellId), e(e)
	{

	}

	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << time << "," << x << "," << y << "," << imsi << "," << e << "," << cellId << "," << rsr;
		return strs.str();
	}

	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
		doc << "Time" << time << "LocationX" << x << "LocationY" << y << "UserID" << (int64_t)imsi
			<< "EventID" << e << "CellID" << (int16_t)cellId << "RSRQ" << rsr;
		return doc;
	}

	static std::string GetFileName()
	{
		return "event_log.csv";
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
	double x;
	double y;
	uint64_t imsi;
	uint16_t cellId;
	uint16_t targetCellId;
	HandoverEventName e;

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	HandoverLog(double time, double x, double y, uint64_t imsi, uint16_t cellId, uint16_t targetCellId, HandoverEventName e)
			: time(time), x(x), y(x), imsi(imsi), cellId(cellId), targetCellId(targetCellId), e(e)
	{

	}

	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << time << "," << x << "," << y << "," << imsi << "," << e << "," << cellId << "," << targetCellId;
		return strs.str();
	}

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
		return "handover_log.csv";
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

	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << time << "," << imsi << "," << cellId << "," << sinr;
		return strs.str();
	}

	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
		doc << "Time" << time << "UserID" << (int64_t)imsi << "CellID" << (int16_t)cellId
			<< "SINR" << sinr;
		return doc;
	}

	static std::string GetFileName()
	{
		return "sinr_log.csv";
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

	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << time << "," << imsi << "," << cellId << "," << throughput;
		return strs.str();
	}

	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
		doc << "Time" << time << "UserID" << (int64_t)imsi << "CellID" << (int16_t)cellId
			<< "Throughput" << throughput;
		return doc;
	}

	static std::string GetFileName()
	{
		return "throughput_log.csv";
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

	///////////////////////////////////
	// PUBLIC METHODS
	///////////////////////////////////

	MainKpiLog(double time, double x, double y, double rsrp, double rsrq, uint64_t imsi, uint16_t cellId)
			: time(time), x(x), y(x), rsrp(rsrp), rsrq(rsrq), imsi(imsi), cellId(cellId)
	{

	}

	std::string ConvertToCSV() override
	{
		std::ostringstream strs;
		strs << time << "," << x << "," << y << "," << imsi << "," << cellId << "," << rsrp << "," << rsrq;
		return strs.str();
	}

	bsoncxx::builder::stream::document ConvertToBSON() override
	{
		bsoncxx::builder::stream::document doc {};
		doc << "Time" << time << "LocationX" << x << "LocationY" << y << "UserID" << (int64_t)imsi
			<< "CellID" << (int16_t)cellId << "RSRP" << rsrp << "RSRQ" << rsrq;
		return doc;
	}



//	bsoncxx::builder::stream::document ConvertToBSON() override
//		{
//
//			int randomNumber = std::rand() % 100;
//
//
//			bsoncxx::builder::stream::document doc {};
//			doc << "Time" << time << "UserThR" << randomNumber << "LocationX" << x << "UserID" << (int)imsi
//				<< "CellID" << (int16_t)cellId << "RSRP" << rsrp << "RSRQ" << rsrq << "SINR" << randomNumber << "LocationY" << y;
//			return doc;
//		}


	static std::string GetFileName()
	{
		return "main_log.csv";
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

	ConfigurationLog(mongocxx::cursor& cursor)
	{
		for(auto view : cursor)
		{
			auto cellId = view["CellId"];
			auto txp = view["TxPower"];
			configurations.push_back(CellConfiguration(cellId.get_int32() - 1, txp.get_double()));
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

//
//			///////////////////////////////////
//			// IF DOUBLE
//			///////////////////////////////////
//
//			auto method = view["normal"];
//			if(method.get_double() == 1)
//			{
//				configurations.push_back(SONEngineConfiguration(cellId.get_double(), SonEngineMethod::Normal));
//				continue;
//			}
//			method = view["outage"];
//			if(method.get_double() == 1)
//			{
//				configurations.push_back(SONEngineConfiguration(cellId.get_double(), SonEngineMethod::Outage));
//				continue;
//			}
//			method = view["coc"];
//			if(method.get_double() == 1)
//			{
//				configurations.push_back(SONEngineConfiguration(cellId.get_double(), SonEngineMethod::COC));
//				continue;
//			}
//			method = view["cco"];
//			if(method.get_double() == 1)
//			{
//				configurations.push_back(SONEngineConfiguration(cellId.get_double(), SonEngineMethod::CCO));
//				continue;
//			}
//			method = view["mro"];
//			if(method.get_double() == 1)
//			{
//				configurations.push_back(SONEngineConfiguration(cellId.get_double(), SonEngineMethod::MRO));
//				continue;
//			}
//			method = view["mlb"];
//			if(method.get_double() == 1)
//			{
//				configurations.push_back(SONEngineConfiguration(cellId.get_double(), SonEngineMethod::MLB));
//				continue;
//			}


			///////////////////////////////////
			// IF INTEGER
			///////////////////////////////////

			auto method = view["normal"];
			if(method.get_int32() == 1)
			{
				configurations.push_back(SONEngineConfiguration(cellId.get_int32(), SonEngineMethod::Normal));
				continue;
			}
			method = view["outage"];
			if(method.get_int32() == 1)
			{
				configurations.push_back(SONEngineConfiguration(cellId.get_int32(), SonEngineMethod::Outage));
				continue;
			}
			method = view["coc"];
			if(method.get_int32() == 1)
			{
				configurations.push_back(SONEngineConfiguration(cellId.get_int32(), SonEngineMethod::COC));
				continue;
			}
			method = view["cco"];
			if(method.get_int32() == 1)
			{
				configurations.push_back(SONEngineConfiguration(cellId.get_int32(), SonEngineMethod::CCO));
				continue;
			}
			method = view["mro"];
			if(method.get_int32() == 1)
			{
				configurations.push_back(SONEngineConfiguration(cellId.get_int32(), SonEngineMethod::MRO));
				continue;
			}
			method = view["mlb"];
			if(method.get_int32() == 1)
			{
				configurations.push_back(SONEngineConfiguration(cellId.get_int32(), SonEngineMethod::MLB));
				continue;
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
