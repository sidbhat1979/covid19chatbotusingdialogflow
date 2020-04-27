from flask import Flask, request, make_response
import json
import os
from flask_cors import cross_origin
from SendEmail.sendEmail import send_email_to_botuser_local, send_email_to_botuser_global
from Upload_to_aws.upload_to_aws import upload_to_aws
from logger import logger
import requests
import matplotlib.pyplot as plt
import uuid
import pandas as pd
import plotly.express as px

app = Flask(__name__)

# geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():

    req = request.get_json(silent=True, force=True)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

# processing the request from dialogflow
def processRequest(req):
    log = logger.Log()
    sessionID=req.get('responseId')
    result = req.get("queryResult")
    user_says=result.get("queryText")
    log.write_log(sessionID, "User Says: "+user_says)
    parameters = result.get("parameters")
    cust_name=parameters.get("cust_name")
    cust_contact = parameters.get("cust_contact")
    cust_email=parameters.get("cust_email")
    cust_pincode= parameters.get("cust_pincode")
    intent = result.get("intent").get('displayName')

    # check for intent. This is the path of local info
    if (intent=='localcovidinfo'):

        # processing the pincode to state
        url = "https://pincode.p.rapidapi.com/"

        payload = "{\"searchBy\":\"pincode\",\"value\":" + str(cust_pincode) +"}"
        headers = {
            'x-rapidapi-host': "pincode.p.rapidapi.com",
            'x-rapidapi-key': "81f2042edamsh5ef9143c6ed40b0p1df119jsn0717257c147e",
            'content-type': "application/json",
            'accept': "application/json"
        }
        response = requests.request("POST", url, data=payload, headers=headers)

        req = response.json()
        #figured the state
        state = req[0]['circle']

        # state_to_iso mapping
        state_to_iso = {
            'Andaman and Nicobar Islands': 'AN',
            'Andhra Pradesh': 'AP',
            'Arunachal Pradesh': 'AR',
            'Assam': 'AS',
            'Bihar': 'BR',
            'Chandigarh': 'CH',
            'Chhattisgarh': 'CT',
            'Dadra and Nagar Haveli': 'DN',
            'Daman and Diu': 'DD',
            'Delhi': 'DL',
            'Goa': 'GA',
            'Gujarat': 'GJ',
            'Haryana': 'HR',
            'Himachal Pradesh': 'HP',
            'Jammu and Kashmir': 'JK',
            'Jharkhand': 'JH',
            'Karnataka': 'KA',
            'Kerala': 'KL',
            'Ladakh': 'LA',
            'Lakshadweep': 'LD',
            'Madhya Pradesh': 'MP',
            'Maharashtra': 'MH',
            'Manipur': 'MN',
            'Meghalaya': 'ML',
            'Mizoram': 'MZ',
            'Nagaland': 'NL',
            'Odisha': 'OR',
            'Puducherry': 'PY',
            'Punjab': 'PB',
            'Rajasthan': 'RJ',
            'Sikkim': 'SK',
            'Tamil Nadu': 'TN',
            'Telangana': 'TG',
            'Tripura': 'TR',
            'Uttar Pradesh': 'UP',
            'Uttarakhand': 'UT',
            'West Bengal': 'WB'
        }

        #figure state_iso
        state_iso = state_to_iso[state]

        #fetching the data for the state
        url = "https://covid19india.p.rapidapi.com/getStateData/" + state_iso

        headers = {
            'x-rapidapi-host': "covid19india.p.rapidapi.com",
            'x-rapidapi-key': "81f2042edamsh5ef9143c6ed40b0p1df119jsn0717257c147e"
        }

        response = requests.request("GET", url, headers=headers)
        res = response.json()
        confirmed = res['response']['confirmed']
        active = res['response']['active']
        recovered = int(res['response']['recovered'])
        deaths = int(res['response']['deaths'])
        id = res['response']['id']
        response_message = "Dear " + cust_name + ", " +  "Please find attached the details of the Covid19 cases in " + state + ". Total No Cases : " + str(confirmed) + ". " + " No of active cases : " + str(active) + ". " + " No of recovered cases : " + str(recovered) + ". " +" No of deaths : " + str(deaths) + ". "

        # Pie chart code for local view
        uid = str(uuid.uuid4().hex)
        file_name = 'LocalReport/report' + uid
        labels = ['active', 'recovered', 'deaths']
        sizes = [active, recovered, deaths]
        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(aspect="equal"))
        #ax = fig.add_axes([0.1, 0.1, 0.6, 0.75])
        total = active + recovered + deaths
        tot = total / 100.0
        autopct = lambda x: "%d" % round(x * tot)
        colors = ('b', 'g', 'r')

        wedges, texts, autotexts = ax.pie(sizes, autopct=autopct, colors=colors,
                                          textprops={'color': 'w'})

        ax.legend(wedges, labels,
                  title="Case Status",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))

        plt.setp(autotexts, size=16, weight="bold")

        ax.set_title("Covid19 Cases in " + state + ":" + str(total), fontsize=18)
        plt.tight_layout()
        plt.savefig(file_name +'.jpg')

        #call function to upload in Amazon S3 bucket
        uploaded = upload_to_aws(file_name+'.jpg', 'covid19sid', file_name+'.jpg', 'jpg')

        email_message=response_message
        send_email_to_botuser_local(cust_email,email_message,uid)
        txt_response = " An email has been sent to your email id with the details. Do you have any further queries?"
        url_link = " https://covid19sid.s3.us-east-2.amazonaws.com/" + file_name +".jpg"
        fulfillmentText = "Please click the link" + url_link + txt_response

       # fulfillmentText= "An email has been sent to your email id with the details. Do you have any further queries?"
        log.write_log(sessionID, "Bot Says: "+fulfillmentText)
        return {
            "fulfillmentText": fulfillmentText
        }
#            "fulfillmentMessages": [
#                {
#                    "text": {
#                        "text": [
#                            fulfillmentText
#                        ]
#                    },
#                    "platform": "TELEGRAM"
#                },
#                {
#                    "payload": {},
#                    "platform": "TELEGRAM"
#                },
#                {
#                    "image": {
#                        "imageUri": "https://covid19sid.s3.us-east-2.amazonaws.com/" + file_name +".jpg"
#                    },
#                    "platform": "TELEGRAM"
#                },
#                {
#                    "image": {
#                        "imageUri": "https://covid19sid.s3.us-east-2.amazonaws.com/" + file_name +".jpg"
#                    },
#                    "platform": "FACEBOOK"
#                },
#                {
#                    "text": {
#                        "text": [
#                            "Please  click the link https://covid19sid.s3.us-east-2.amazonaws.com/" + file_name +".jpg"
#                        ]
#                    }
#                },
#                {
#                    "text": {
#                        "text": [
#                            ""
#                        ]
#                    }
#                },
#                {
 #                   "payload": {}
 #               }
 #           ]
 #       }

    elif (intent=='globalcovidinfo'):

        #calling API to fetch global data

        url = "https://covid-193.p.rapidapi.com/statistics"

        headers = {
            'x-rapidapi-host': "covid-193.p.rapidapi.com",
            'x-rapidapi-key': "81f2042edamsh5ef9143c6ed40b0p1df119jsn0717257c147e"
        }

        response = requests.request("GET", url, headers=headers)

        res = response.text
        data = json.loads(res)
        firstlevel = data['response']
        country = []
        total_cases = []
        active_cases = []
        recovered_cases = []
        all_deaths = []
        deaths = []
        for all_rec in firstlevel:
            country.append((all_rec['country']))
            total_cases.append(all_rec['cases']['total'])
            active_cases.append(all_rec['cases']['active'])
            recovered_cases.append(all_rec['cases']['recovered'])
            all_deaths.append(all_rec['deaths'])
        for deaths_row in all_deaths:
            deaths.append(deaths_row['total'])
        data_new = pd.DataFrame({'country': country,
                                 'total_cases': total_cases,
                                 'active_cases': active_cases,
                                 'recovered_cases': recovered_cases,
                                 'deaths': deaths})
        fig = px.choropleth(data_new, locations="country",
                            locationmode="country names",
                            color="total_cases",
                            hover_name="country",
                            hover_data=["total_cases", "active_cases", "recovered_cases", "deaths"],
                            range_color=[0, 1000000],
                            title="World View of Covid19 cases"
                            )
        uid = str(uuid.uuid4().hex)
        file_name = 'GlobalReport/report' + uid
        fig.write_html(file_name + ".html")
        #fig.write_image(file_name + ".jpg")

        #call function to upload in Amazon S3 bucket
        uploaded = upload_to_aws(file_name+'.html', 'covid19sid', file_name+'.html', 'html')

        response_message = "Dear " + cust_name + " ," + "Please find attached the details of Covid19 cases Globally. "
        email_message=response_message
        send_email_to_botuser_global(cust_email,email_message,uid)
        txt_response = " An email has been sent to your email id with the details. Do you have any further queries?"
        url_link = " https://covid19sid.s3.us-east-2.amazonaws.com/" + file_name +".html"
        fulfillmentText = "Please click the link" + url_link + txt_response
        log.write_log(sessionID, "Bot Says: "+fulfillmentText)
        return {
            "fulfillmentText": fulfillmentText
        }
#            "fulfillmentMessages": [
#                {
#                    "text": {
#                        "text": [
#                            "Please click the link" + url_link
#                        ]
#                    },
#                    "platform": "TELEGRAM"
#                },
#                {
#                    "payload": {},
#                    "platform": "TELEGRAM"
#                },
#                {
#                    "image": {
#                        ""
#                    },
#                    "platform": "TELEGRAM"
#                },
#                {
#                    "image": {
#                        "imageUri": ""
#                    },
#                    "platform": "FACEBOOK"
#                },
#                {
#                    "text": {
#                        "text": [
#                            "Please click the link" + url_link
#                        ]
#                    }
#                },
#                {
#                    "text": {
#                        "text": [
#                            ""
#                        ]
#                    }
#                },
#                {
#                    "payload": {}
#                }
#            ]
#        }
    else:
        log.write_log(sessionID, "Bot Says: " + result.fulfillmentText)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=True, port=port, host='0.0.0.0')
