from pmkoalas.read import read_xes_complex
from pmkoalas.export import export_to_xes_complex
from pmkoalas._logging import enable_logging, debug, info
from logging import DEBUG, INFO
from pmkoalas.complex import ComplexTrace, ComplexEventLog, ComplexEvent

from os.path import join 
from dataclasses import dataclass
from datetime import datetime,timedelta

from typing import List


@dataclass
class Point():
    time:datetime
    value:float

    def __repr__(self) -> str:
        return f"({self.time}, {self.value})"
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __gte__(self, other) -> bool:
        return self.time >= other.time
    
    def __lte__(self, other) -> bool:
        return self.time <= other.time
    
    def __lt__(self,other) -> bool:
        return self.time < other.time

    def __gt__(self,other) -> bool:
        return self.time > other.time


FINE_ADDED = "Create Fine"
FINE_AMOUNT_ADD = ["Create Fine", "Add penalty"]
FINE_AMOUNT_ADD_ATTR = "amount"
FINE_AMOUNT_REDUCE = ["Payment"]
FINE_AMOUNT_REDUCE_ATTR = "paymentAmount"
RESOLVE_FINE = ["Send for Credit Collection"]
TIME_ATTR = "time:timestamp"

def extract_time(trace, id):
    return extract_attr(trace, id, TIME_ATTR)

def extract_attr(trace, id, attr):
    return trace[id].data()[attr]

@enable_logging
def main():
    log = read_xes_complex(join(".","road_fines.xes"),debug=True)

    unresolved:List[Point] = []
    famount:List[Point] = []

    # iterate through log to collect information
    # collect when fines are issued and resolved
    # collect the amount of fine issued, and track when payments occur
    curr_var = 1
    for variant,instances in log.__iter__():
        # loop through variant to see if activities come up
        info(f"working on {curr_var}/{log.get_nvariants()}")
        curr_var += 1
        info(f"{variant=}")
        interested = []
        for id,act in enumerate(variant):
            if act in FINE_AMOUNT_ADD + FINE_AMOUNT_REDUCE + RESOLVE_FINE:
                interested.append(id)
        info(f"{interested=}")
        # for each instance look at interesting
        # add points as needed
        for instance in instances:
            total_fine = 0
            total_paid = 0
            # debug(f"{instance=}")
            for id in interested:
                # if act is fine, then add unresolved and fine amount
                if instance[id].activity() == FINE_ADDED:
                    p = Point(extract_time(instance,id), 1)
                    unresolved.append(p)
                elif instance[id].activity() in RESOLVE_FINE:
                    p = Point(extract_time(instance,id), -1)
                    unresolved.append(p)
                    p = Point(
                        extract_time(instance,id),
                        total_fine * -1
                    ) 
                    famount.append(p)
                # if act is either payment or penalty add to famount
                if  instance[id].activity() in FINE_AMOUNT_ADD:
                    p = Point(
                        extract_time(instance,id),
                        extract_attr(instance, id, FINE_AMOUNT_ADD_ATTR)
                    ) 
                    famount.append(p)
                    total_fine += extract_attr(instance, id, FINE_AMOUNT_ADD_ATTR)
                elif instance[id].activity() in FINE_AMOUNT_REDUCE:
                    p = Point(
                        extract_time(instance,id),
                        extract_attr(instance, id, FINE_AMOUNT_REDUCE_ATTR) * -1.0
                    ) 
                    famount.append(p)
                    total_paid += extract_attr(instance, id, FINE_AMOUNT_REDUCE_ATTR)
            # if fined was paid then reduce
            if  total_fine == total_paid:
                # reduce the number of unresolved
                p = Point(instance[instance._len-1].data()["time:timestamp"], -1) 
                unresolved.append(p)
                debug("reduced unresolved fine.")
            debug(f"{unresolved[-5:]=}")
            debug(f"{famount[-5:]=}")
            debug(f"fine={total_fine}, paid={total_paid}")
        info(f"curr size {len(unresolved)=} and {len(famount)=}")
    # now order lists and make them cummlative
    unresolved = sorted(unresolved)
    famount = sorted(famount)
    # export list as exogenous datasets
    events = [] 
    times = dict()
    event_id = 1
    cvalue = 0
    info("exporting unresolved fines...")
    while len(unresolved) > 0:
        p = unresolved.pop(0)
        cvalue += p.value
        times[p.time] = cvalue
        del p
    # for each trace, create subset that outlines the last 14 days
    traces = []
    trace_id = 1
    timedates = times.keys()
    for variant, insts in log.__iter__():
        for trace in insts:
            info(f"handling trace :: {trace_id}/{len(log)}")
            events = []
            if (len(trace) > 0):
                start = trace[0].data()["time:timestamp"] - timedelta(14,0,0,0,0,0,0)
                end = trace[len(trace)-1].data()["time:timestamp"]
                subset = [ time for time in timedates if time > start and time < end]
                subset = sorted(subset)
                event_id = 1
                for time in subset:
                    events.append(
                        ComplexEvent(
                        f"exogenous_data_point_{event_id:06d}",
                        data={
                            'time:timestamp' :  time,
                            'exogenous:value' : times[time]
                        }
                        )
                    )
            trace_id+=1
            traces.append(
                ComplexTrace(
                    events, 
                    {
                        "concept:name" : trace.data()["concept:name"]
                    }
                )
            )             
    xdataset = ComplexEventLog(
        traces,
        {
            'exogenous:dataset' : "TRUE"
        },
        "exogenous dataset unresolved fines")
    export_to_xes_complex(join(".","exogenous_dataset_unresolved_fines.xes"), xdataset, debug=True, debug_level=INFO)

    events = [] 
    times = dict()
    event_id = 1
    cvalue = 0
    info("exporting unpaid fines...")
    while len(famount) > 0:
        p = famount.pop(0)
        cvalue += p.value
        times[p.time] = cvalue
        del p
    # for each trace, create subset that outlines the last 14 days
    traces = []
    trace_id = 1
    timedates = times.keys()
    for variant, insts in log.__iter__():
        for trace in insts:
            info(f"handling trace :: {trace_id}/{len(log)}")
            events = []
            if (len(trace) > 0):
                start = trace[0].data()["time:timestamp"] - timedelta(14,0,0,0,0,0,0)
                end = trace[len(trace)-1].data()["time:timestamp"]
                subset = [ time for time in timedates if time > start and time < end]
                subset = sorted(subset)
                event_id = 1
                for time in subset:
                    events.append(
                        ComplexEvent(
                        f"exogenous_data_point_{event_id:06d}",
                        data={
                            'time:timestamp' :  time,
                            'exogenous:value' : times[time]
                        }
                        )
                    )
            traces.append(
                ComplexTrace(
                    events, 
                    {
                        "concept:name" : trace.data()["concept:name"]
                    }
                )
            )

    xdataset = ComplexEventLog(
        traces,
        {
            'exogenous:dataset' : "TRUE"
        },
        "exogenous dataset unpaid fines")
    export_to_xes_complex(join(".","exogenous_dataset_unpaid_fines.xes"), xdataset, debug=True, debug_level=INFO)
    info("completed extracting datasets.")

if __name__ == "__main__":
    main(debug=True, debug_level=INFO)
