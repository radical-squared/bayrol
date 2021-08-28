# Home Assistant Bayrol Pool Relax sensor (Custom component) 

This is Home Assistant's custom sensor that retrieves data from Bayrol cloud and makes it available in Home Assistant. It creates sensor.bayrol entity that shows system's online/offline status, as well as water redox and pH levels and errors as attributes. The entity can auto dismiss beeping errors if you set input_boolean.bayrol_autodismiss to true.
    

### Authentication issue
I cannot get user authentication to work with regular username and password. Instead, one needs to use web browser's developer tools to retrieve "authuser", "authpass" and "cid" from cookie set by Bayrol cloud.   


### Home Assistant Setup
To install copy the directory to your custom_components folder, restart HA and then add the following to your configuration.yaml file:
```
sensor:
  - platform: bayrol
    name: bayrol
    authuser: your_username
    authpass: your_authpass_set_by_cloud
    cid: system_id
    autodismiss: false
    autodismiss_entity: input_boolean.bayrol_autodismiss
    
  - platform: template
    sensors:
      pool_redox:
        unit_of_measurement: "mV"
        value_template: "{{state_attr('sensor.bayrol','rx')}}"
      pool_ph:
        unit_of_measurement: "pH"
        value_template: "{{state_attr('sensor.bayrol','pH')}}"        
  
input_boolean:
  bayrol_autodismiss:
    name: Autodismiss bayrol errors  
```
  
