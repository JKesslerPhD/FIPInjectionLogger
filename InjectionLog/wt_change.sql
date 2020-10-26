Select 
	cat_weight, 
	days, 
	pct_change, 
	injection_amount, 
	gs_brand, 
	coalesce(InjectionLog_usergs.price,InjectionLog_gsbrand.price) as price,
	case 
		when wt_units ="kg" then starting_wt*2.2
		else starting_wt
	end as start_wt 
from
	(Select 
		old.cat_weight as starting_wt, 
		round((InjectionLog_injectionlog.cat_weight-old.cat_weight)/old.cat_weight*100,1) as pct_change, 
		round(julianday(InjectionLog_injectionlog.injection_time)-julianday(old.injection_time),0) as days, 
		* 
	from 
		InjectionLog_injectionlog,
		(select 
			min(injection_time) as injection_time, 
			min(cat_weight) as cat_weight, 
			cat_name_id 
		from 
			InjectionLog_injectionlog 
		group by cat_name_id) as old 
	where 
		old.cat_name_id = InjectionLog_injectionlog.cat_name_id) 
	left join InjectionLog_gsbrand on InjectionLog_gsbrand.brand=gs_brand
	left join InjectionLog_usergs on InjectionLog_usergs.brand=gs_brand
	where 
		days>0 and 
		pct_change>0

