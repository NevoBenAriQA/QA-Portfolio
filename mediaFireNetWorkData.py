import time
import pandas as pd
from selenium import webdriver
from browsermobproxy import Server


# Function that will handle messages written to the console
def log_console_messages(driver):
    entries = []
    for entry in driver.get_log('browser'):
        entries.append({'level': entry['level'], 'message': entry['message']})
    df = pd.DataFrame(entries)

# Output console data to CSV file
    df.to_csv('console_errors.csv', index=False)


driver = None
server = None

try:
    # Setup browsermob proxy server
    server = Server("C:\\...")
    server.start()
    proxy = server.create_proxy()

    # Setup Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--proxy-server={}".format(proxy.proxy))
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    # Open MediaFire website
    driver = webdriver.Chrome(options=chrome_options)
    proxy.new_har("mediafire", options={'captureHeaders': True, 'captureContent': True})
    driver.get("https://mediafire.com/")

    # Collect console errors
    log_console_messages(driver)

    # Collect network data
    network_data = proxy.har
    data = []
    for entry in network_data['log']['entries']:
        request = entry['request']
        response = entry['response']
        data.append({
            'method': request['method'],
            'url': request['url'],
            'httpVersion': request['httpVersion'],
            'status': response['status'],
            'statusText': response['statusText'],
            'requestHeaders': request['headers'],
            'responseHeaders': response['headers'],
        })

    # Output network data to CSV file
    df = pd.DataFrame(data)
    df.to_csv('network_data.csv', index=False)

    # Wait for 5 seconds before closing the browser
    time.sleep(5)
finally:

    # Close browser and stop proxy server
    if driver:
        driver.quit()
    if server:
        server.stop()

print("Network Data and Console Errors have been collected and saved to CSV.")
