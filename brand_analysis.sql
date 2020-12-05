Select * from (

Select gs_brand, week, avg(cat_behavior_today) as avg_behavior, count(*) as records from(
Select *, 
(cast(days/7 as int)+1)  as week,
case 
	when wt_units = "lb" then round(dose/(cat_weight/2.2),0)
	when wt_units = "kg" then round(dose/cat_weight,0)
end as dosage

	
 from (
Select gs_brand, 

round(julianday(injection_time) - julianday(treatment_start),0) as days,
concentration * injection_amount as dose,
cat_behavior_today,
wt_units,
cat_weight
from InjectionLog_injectionlog, InjectionLog_cats, injectionLog_gsbrand where 
	InjectionLog_injectionlog.cat_name_id=InjectionLog_cats.id and
	InjectionLog_gsbrand.brand = InjectionLog_injectionlog.gs_brand
and InjectionLog_cats.owner_id not in (Select user_id from InjectionLog_userextension where test_account = 1)) as foo,
(Select gs_brand as brand, count(*) as total_observations, count(distinct(cat_name_id)) as logged_cats from InjectionLog_injectionlog, InjectionLog_cats 
	where  InjectionLog_cats.owner_id not in (Select user_id from InjectionLog_userextension where test_account = 1) and InjectionLog_injectionlog.cat_name_id = InjectionLog_cats.id group by gs_brand) as log

where log.brand = foo.gs_brand) group by week, gs_brand) where records>7*5