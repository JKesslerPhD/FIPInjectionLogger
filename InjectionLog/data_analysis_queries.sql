
Select * from (
select 
	username,
	count(InjectionLog_injectionlog.id) as LogEntries, 
	cast(julianday(max(InjectionLog_injectionlog.injection_time)) -	julianday(min(InjectionLog_injectionlog.injection_time)) as int) as days_from_logs,
	cast(julianday(date('now')) -	julianday(min(InjectionLog_injectionlog.injection_time)) as int) as days_from_time,
	round((julianday(date('now')) - julianday(birthday))/365,1) as cat_age,
	InjectionLog_cats.*
	
from 
	InjectionLog_cats, InjectionLog_injectionlog, auth_user
where 
	injectionlog_cats.owner_id not in (Select user_id from InjectionLog_userextension where test_account =1) and 
	InjectionLog_cats.id = InjectionLog_injectionlog.cat_name_id and
	InjectionLog_injectionlog.active=1 and
	injectionLog_cats.owner_id = auth_user.id
group by injectionLog_cats.id ) where LogEntries>2