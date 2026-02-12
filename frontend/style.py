style="""
<style>
div[data-testid="stAppDeployButton"] { display: none !important; }
div[data-testid="stMainMenu"] { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
div[data-testid="stMainBlockContainer"]{
  padding: 0 !important; 
}
section.main > div.block-container{
  padding: 0 !important;
}
div[data-testid="stAppViewContainer"]{
  padding: 0 !important;
}
.st-key-pills1>div>div>button{
    width: 300px;
    height: 50px;
    margin: 10px 0 10px 0;
}   
#podderzhka-sotrudnikov-po-vnutrennim-normativnym-dokumentam{
    margin-bottom: 20px;
    padding-left:20px;
    text-align: center;
}
.stVerticalBlock {
    display: flex;
    align-items: center;
}
            
div[data-widget-key="pills1"] div[data-testid="stPills"] button{
  box-sizing: border-box;
  width: 100%;
  min-height: 56px;
  padding: 12px 24px !important;
  border: 2px solid var(--gray-300) !important; 
  border-radius: 9999px !important;
  background: transparent !important;
  font-weight: 500 !important;                   
  margin: 20px 0 !important;
}

div[data-widget-key="pills1"] div[data-testid="stPills"] button[aria-pressed="true"],
div[data-widget-key="pills1"] div[data-testid="stPills"] button:hover,
div[data-widget-key="pills1"] div[data-testid="stPills"] button:focus{
  border-width: 2px !important;                  
  padding: 12px 24px !important;                 
  font-weight: 500 !important;                 
  outline: none !important;
  box-shadow: none !important;
  border-color: #ef4444 !important;             
}            
div[data-widget-key="pills1"] div[data-testid="stPills"] button { min-width: 240px !important; }   
</style>
"""