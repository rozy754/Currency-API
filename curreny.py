from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import requests

class Message(Model):
    message: str

currency_agent=Agent(
    name="currency_agent",
    port=8000,
    seed="currency_secret_phrase",
    endpoint=["https://127.0.0.1:8000/submit"],

)    

fund_agent_if_low(currency_agent.wallet.address())


base_currency=input("enter the base currency(eg., USD):").upper()
target_currencies={}
num_targets=int(input("enter the number of target currencies: "))
for i in range(num_targets):
    target_currency=input(f"Enter target currency{i+1}(e.g., EUR):").upper()
    min_value=float(input(f"Enter the desired minimum value of the {target_currency}:"))
    max_value=float(input(f"Enter the maximum value of the {target_currency}:"))
    target_currencies[target_currency]={"min": min_value,"max":max_value}

API_URL =f"https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_ibC51c14IvUcpZg9wths4bha0hHJ0xQHw42SvBCe{base_currency}"

def get_exchange_rates(base_currency):
    try:
        response=requests.get(API_URL)
        data=response.json()

        if response.status_code==200:
            return data["Conversion_rates"]
        else:
            print(f"failed to fetch exchange rates. Status code:{response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching exchange rate data:{e}")
        return None
    
def monitor_exchange_rates():
    exchange_rates=get_exchange_rates(base_currency)
    if exchange_rates is not None:
        alerts=[]
        for currency, limits in target_currencies.items():
            rate=exchange_rates.get(currency)
            if rate is not None:
                if rate<limits["min"]:
                    alerts.append(f"{currency}rate is below the desired minimum({limits['min']}).")
                elif rate>limits["max"]:
                    alerts.append(f"{currency}rate exceeded the maximum limit({limits['max']}).")
        return alerts
    else:
        return []
    
async def notify_user(alert):
    
    
    for message in alert:
        servicePlanId = "b9c54b36192b42f393a94d1aed05e13c"
        apiToken ="b0cbe7bdac8c4a368aa0030d10d74eb6f"
        sinchNumber ="+447520651166"
        toNumber="+918954381456"
        url="https://us.sms.api.sinch.com/xms/v1/"+servicePlanId+"/batches"

        payload ={
        "from": sinchNumber,
        "to":[
            toNumber
        ],
        "body":message
        }
        headers={
            "Content-Type":"application/json",
            "Authorization": "Bearer"+ apiToken
        }
        
        response= requests.post(url,json=payload, headers=headers)

        data=response.json()
        print(data)


@currency_agent.on_interval(period=3600.0)
async def currency_monitor(ctx:Context):
    alerts= monitor_exchange_rates()
    ctx.logger.info(alerts)
    if alerts:
        await notify_user(alerts)

if __name__=="__main__":
    currency_agent.run()



