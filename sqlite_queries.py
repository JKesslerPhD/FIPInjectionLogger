import sqlalchemy as sql
import pandas as pd
import statsmodels.formula.api as smf
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.express as px
from plotly import colors
import numpy as np
import json
import os

class Database():
    def __init__(self, db_file="db.sqlite3"):
        db_file = os.path.dirname(__file__)+"/"+db_file
        self.engine = sql.create_engine('sqlite:///%s' % db_file)
        self.fip_stats = None
        self.weight = None
        self.summary = None
        self.quality = None
    
    def get_cat_quality(self):
        query = """
        Select 
            *, 
            (cast(days/7 as int)+1)  as week,
            case 
               	when wt_units = "lb" then round(dose/(cat_weight/2.2),0)
               	when wt_units = "kg" then round(dose/cat_weight,0)
            end as dosage
        
        from 
            (
                Select 
                    gs_brand, 
                    round(julianday(injection_time) - julianday(treatment_start),0) as days,
                    concentration * injection_amount as dose,
                    cat_behavior_today,
                    wt_units,
                    cat_weight
                from 
                    InjectionLog_injectionlog, InjectionLog_cats, injectionLog_gsbrand 
                where 
                   	InjectionLog_injectionlog.cat_name_id=InjectionLog_cats.id and
                   	InjectionLog_gsbrand.brand = InjectionLog_injectionlog.gs_brand
                    and InjectionLog_cats.owner_id not in (Select user_id from InjectionLog_userextension where test_account = 1)
            ) as foo,
            (
                Select 
                    gs_brand as brand, 
                    count(*) as total_observations, 
                    count(distinct(cat_name_id)) as logged_cats 
                from 
                    InjectionLog_injectionlog, InjectionLog_cats 
           	where  
           	    InjectionLog_cats.owner_id not in (Select user_id from InjectionLog_userextension where test_account = 1) and 
           	    InjectionLog_injectionlog.cat_name_id = InjectionLog_cats.id group by gs_brand
       	    ) as log
        
        where 
            log.brand = foo.gs_brand
        """
        if not self.quality:
            self.quality = df = pd.read_sql(query, self.engine)

        return df

    def get_weight(self):
        query = """
        Select
       	cat_weight,
       	days,
       	pct_change,
       	injection_amount,
       	gs_brand,
       	(case when admin_method = "Oral" then
	   cast(price as float)/(concentration) 
	else
	   cast(price as float)/(concentration*5)
	end) as price,
       	round(case
      		when wt_units ="kg" then starting_wt*2.2
      		else starting_wt
       	end,1) as start_wt,
       	pct_change/days*100 as ratio,
       	round((julianday(date('now')) - julianday(birthday))/365,0) as cat_age
        from
       	(Select
      		old.cat_weight as starting_wt,
      		round((InjectionLog_injectionlog.cat_weight-old.cat_weight)/old.cat_weight*100,0)/100 as pct_change,
      		round(julianday(InjectionLog_injectionlog.injection_time)-julianday(old.injection_time),0) as days,
      		coalesce(InjectionLog_usergs.price,InjectionLog_gsbrand.price) as price,
      		coalesce(InjectionLog_usergs.concentration,InjectionLog_gsbrand.concentration) as concentration,
      		*
       	from
      		InjectionLog_injectionlog,
      		InjectionLog_cats,
      		(select
     			min(injection_time) as injection_time,
     			min(cat_weight) as cat_weight,
     			cat_name_id
      		from
     			InjectionLog_injectionlog
      		group by cat_name_id) as old
       	left join InjectionLog_gsbrand on InjectionLog_gsbrand.brand=gs_brand
       	left join InjectionLog_usergs on InjectionLog_usergs.brand=gs_brand
       	where
       		InjectionLog_cats.owner_id not in (Select user_id from InjectionLog_userextension where test_account =1) and
      		old.cat_name_id = InjectionLog_injectionlog.cat_name_id and
      		InjectionLog_cats.id = InjectionLog_injectionlog.cat_name_id )
   	where days>0 and ratio <5 and cat_age <10
   	"""
        if not self.weight:
            self.weight = df = pd.read_sql(query, self.engine)

        return df

    def get_summary(self):
        query = """

        Select * from (
        select
       	username,
	relapse_start,
       	count(InjectionLog_injectionlog.id) as LogEntries,
       	cast(julianday(max(InjectionLog_injectionlog.injection_time)) -	julianday(min(InjectionLog_injectionlog.injection_time)) as int) as days_from_logs,
	case 
	   when relapse_start not NULL then
		cast(julianday(date('now')) -	julianday(relapse_start) as int)
	   else
		cast(julianday(date('now')) -	julianday(min(InjectionLog_injectionlog.injection_time))-extended_treatment as int) 
	end as days_from_time,
       	round((julianday(date('now')) - julianday(birthday))/365,0) as cat_age,
       	(max(InjectionLog_injectionlog.cat_weight)-min(InjectionLog_injectionlog.cat_weight))/min(InjectionLog_injectionlog.cat_weight)/cast(julianday(max(InjectionLog_injectionlog.injection_time)) -	julianday(min(InjectionLog_injectionlog.injection_time)) as int)*100 as cat_weight,
       	InjectionLog_cats.*

        from
       	InjectionLog_cats, InjectionLog_injectionlog, auth_user
		left join InjectionLog_relapsedate on InjectionLog_cats.id = InjectionLog_relapsedate.cat_name_id
        where
       	injectionlog_cats.owner_id not in (Select user_id from InjectionLog_userextension where test_account =1) and
       	InjectionLog_cats.id = InjectionLog_injectionlog.cat_name_id and
       	InjectionLog_injectionlog.active=1 and
       	injectionLog_cats.owner_id = auth_user.id
        group by injectionLog_cats.id ) where LogEntries>2
        """
        if not self.summary:
            self.summary = df = pd.read_sql(query, self.engine)

        return df
    
    def get_relapse_stats(self):
        query = """
        Select 
	round(julianday('now') - julianday(treatment_start),0) as days_since_start,
	round(julianday(relapse_start)-julianday(treatment_start),0) as days_before_relapse,
	case
		when round(julianday(relapse_start)-julianday(treatment_start),0) > 84 THEN
			round(julianday(relapse_start)-julianday(treatment_start)-84,0)
		ELSE
			0
	end as days_into_observation,
	round(julianday('now') - julianday(relapse_start),0) as days_since_relapse,
	* from InjectionLog_relapsedate, InjectionLog_cats where 
	InjectionLog_relapsedate.cat_name_id == InjectionLog_cats.id and 
	InjectionLog_cats.owner_id not in (Select user_id from InjectionLog_userextension where test_account = 1) group by cat_name_id order by relapse_start desc
	"""

    def get_fip_stats(self):
        query = """
        Select
            fip_type as FIPType,
  		sum(case
 			when neuro=0 and ocular =0 then 1
 			else 0
  		end) as traditional,
  		sum(case
 			when neuro=0 and ocular=1 then 1
 			else 0 end) as ocular,
  		sum(case
  		when neuro=1 and ocular=0 then 1
  		else 0 end) as neuro,
  		sum(case when neuro=1 and ocular=1 then 1
  		else 0 end) as neuro_and_ocular

        from
            InjectionLog_cats
                where
           	injectionlog_cats.owner_id not in (Select user_id from InjectionLog_userextension where test_account =1)
        group by fip_type
        """
        if not self.fip_stats:
            self.fip_stats = df = pd.read_sql(query, self.engine)

        return df


