import {
  Activity,
  Factory,
  Timer,
  Gauge,
  Boxes,
  Cpu
} from "lucide-react";

export default function FactorySummary({ data }) {

if (!data) return null;

const cards = [
{
title:"Production",
value:data.total_production_count,
icon:<Factory size={18}/>
},
{
title:"Avg Rate",
value:`${data.avg_production_rate} u/hr`,
icon:<Gauge size={18}/>
},
{
title:"Worker Util",
value:`${data.avg_worker_utilization_pct}%`,
icon:<Activity size={18}/>
},
{
title:"Station Util",
value:`${data.avg_station_utilization_pct}%`,
icon:<Cpu size={18}/>
},
{
title:"Events",
value:data.total_events_processed,
icon:<Boxes size={18}/>
},
{
title:"Active Time",
value:fmt(data.total_active_time_secs),
icon:<Timer size={18}/>
}
];

return (

<div className="grid md:grid-cols-3 lg:grid-cols-6 gap-5 mb-8">

{cards.map(c=>(

<div
key={c.title}
className="bg-white rounded-xl shadow hover:shadow-lg transition p-5"
>

<div className="flex justify-between mb-3">

<p className="text-xs text-gray-400 uppercase">
{c.title}
</p>

<div className="text-blue-600">
{c.icon}
</div>

</div>

<h2 className="text-2xl font-bold text-slate-900">
{c.value}
</h2>

</div>

))}

</div>

);
}

function fmt(sec){

if(!sec) return "0h";

const h=Math.floor(sec/3600);
const m=Math.floor((sec%3600)/60);

return `${h}h ${m}m`;

}