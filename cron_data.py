import sqlalchemy as sql
import pandas as pd
import statsmodels.formula.api as smf
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.express as px
import json
import os

class Database():
    def __init__(self, db_file="db.sqlite3"):
        db_file = os.path.dirname(__file__)+"/"+db_file
        self.engine = sql.create_engine('sqlite:///%s' % db_file)
        self.fip_stats = None
        self.weight = None
        self.summary = None

    def get_weight(self):
        query = """
        Select
       	cat_weight,
       	days,
       	pct_change,
       	injection_amount,
       	gs_brand,
       	cast(price as float)/(concentration*5) as price,
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
       	count(InjectionLog_injectionlog.id) as LogEntries,
       	cast(julianday(max(InjectionLog_injectionlog.injection_time)) -	julianday(min(InjectionLog_injectionlog.injection_time)) as int) as days_from_logs,
       	cast(julianday(date('now')) -	julianday(min(InjectionLog_injectionlog.injection_time)) as int) as days_from_time,
       	round((julianday(date('now')) - julianday(birthday))/365,0) as cat_age,
       	(max(InjectionLog_injectionlog.cat_weight)-min(InjectionLog_injectionlog.cat_weight))/min(InjectionLog_injectionlog.cat_weight)/cast(julianday(max(InjectionLog_injectionlog.injection_time)) -	julianday(min(InjectionLog_injectionlog.injection_time)) as int)*100 as cat_weight,
       	InjectionLog_cats.*

        from
       	InjectionLog_cats, InjectionLog_injectionlog, auth_user
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


class Analysis():
    def __init__(self):
        pass

    def save_file(self, json_dict, filename):
        with open(filename,'w') as json_file:
            json.dump(json_dict, json_file)

    def generate_fip_summary(self, fip_summary):

        total_cats = fip_summary["traditional"]+fip_summary["ocular"]+fip_summary["neuro"]+fip_summary["neuro_and_ocular"]
        fip_summary = pd.melt(fip_summary,id_vars="FIPType", var_name="Symptoms")
        fip_fig = px.bar(fip_summary, x="FIPType", y="value", color="Symptoms", title="Frequency of Symptoms by FIP Type")
        fip_fig.update_layout(
        yaxis_title="Number of cats with symptoms")

        fip_div = plot(fip_fig, output_type='div', include_plotlyjs="cdn")

        return {"total_cats":total_cats.to_dict(),"graph":str(fip_div)}

    def generate_summary_stats(self,summary):
        cat_age = summary.groupby("cat_age").count()
        cat_age["age"] = cat_age.index
        cat_age["counts"]=cat_age["name"]
        age_fig = px.bar(cat_age,x="age", y="counts", title="Cats with FIP by age")

        age_div = plot(age_fig,output_type='div', include_plotlyjs="cdn")

        return {"graph":age_div}

    def generate_weight_figure(self,weight):
        fig = go.Figure()
        fig = px.scatter(weight, x=weight["days"], y=weight["pct_change"]*100,
                        opacity=0.8, color=weight["start_wt"]
                        )
        fig.update_layout(
        title="Percent change in cat's weight since starting treatment for all logged data",
        xaxis_title="Days of Treatment",
        yaxis_title="Pct Change from Cat's Starting Weight")

        wt_div = plot(fig, output_type='div', include_plotlyjs="cdn")
        
        weight["cat_age"] = weight["cat_age"].astype('float')

        model = smf.ols(formula="pct_change ~ 0 + start_wt + days + cat_age", data=weight).fit()
        mult = model.params["days"]
        try:
            ints = model.params["Intercept"]
        except:
            ints = 0
        daily_price = weight["price"].mean()
        stwt = model.params["start_wt"]
        age = model.params["cat_age"]

        model_dict = {"ints":ints,"stwt":stwt,"mult":mult, "age":age, "daily_price":daily_price}

        return {"graph":wt_div,"model":model_dict}

    def generate_cat_treatment_dist(self, summary):
        duration_df = summary[summary["days_from_time"]<=84].groupby("days_from_time").count()
        cats84 = summary[summary["days_from_time"]>84].count()[0]
        duration_df["Days since starting"]=duration_df.index
        duration_df["counts"]=duration_df["name"]
        duration_fig = px.bar(duration_df, x="Days since starting", y="counts", title="# of cats with data being logged relative to how many days ago treatment was started")

        duration_fig.update_layout(
        xaxis_title="Days since starting treatment",
        yaxis_title="# of cats with data on this site")
        
        duration_div=plot(duration_fig,output_type="div", include_plotlyjs="cdn")

        return {"graph":duration_div, "total_cats":str(cats84)}

def generate_graphs(output_file="data_output.txt"):
    data = Database()
    an   = Analysis()

    weight      = data.get_weight()
    summary     = data.get_summary()
    fip_summary = data.get_fip_stats()

    graph_summary = an.generate_summary_stats(summary)
    graph_distribution = an.generate_cat_treatment_dist(summary)
    graph_fip_stats = an.generate_fip_summary(fip_summary)
    graph_wt_change = an.generate_weight_figure(weight)

    combined_dict = {
        "summary":graph_summary,
        "distribution":graph_distribution,
        "fip_stats":graph_fip_stats,
        "weight":graph_wt_change,
    }

    an.save_file(combined_dict,output_file)

def read_data(filename):
    with open(filename) as json_file:
        data = json.load(json_file)

    return data

if __name__=="__main__":
    directory=os.path.dirname(__file__)
    generate_graphs(directory+"/data_output.txt")
