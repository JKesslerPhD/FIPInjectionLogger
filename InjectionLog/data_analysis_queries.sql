

select 
	count(InjectionLog_injectionlog.id) as LogEntries, 
	cast(julianday(max(InjectionLog_injectionlog.injection_time)) -	julianday(min(InjectionLog_injectionlog.injection_time)) as int) as log_entries, 
	InjectionLog_cats.* 
from 
	InjectionLog_cats, InjectionLog_injectionlog 
where 
	injectionlog_cats.owner_id not in (Select user_id from InjectionLog_userextension where test_account =1) and 
	InjectionLog_cats.id = InjectionLog_injectionlog.cat_name_id 
group by injectionLog_cats.id 