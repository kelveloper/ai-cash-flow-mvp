import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.get("http://localhost:8000")
    yield driver
    driver.quit()

def test_transaction_list_rendering(driver):
    # Wait for transaction list to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "transactions-table"))
    )
    
    # Check if transactions are displayed
    transactions = driver.find_elements(By.CSS_SELECTOR, ".transactions-table tbody tr")
    assert len(transactions) > 0
    
    # Check transaction structure
    first_transaction = transactions[0]
    assert first_transaction.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text  # Date
    assert first_transaction.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text  # Description
    assert first_transaction.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text  # Category
    assert first_transaction.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text  # Amount

def test_transaction_filtering(driver):
    # Wait for search input
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "transactionSearch"))
    )
    
    # Test search functionality
    search_input.send_keys("Salary")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".transactions-table tbody tr"))
    )
    
    # Test type filter
    type_filter = driver.find_element(By.ID, "transactionStatus")
    type_filter.click()
    type_filter.find_element(By.CSS_SELECTOR, "option[value='posted']").click()
    
    # Test category filter
    category_filter = driver.find_element(By.ID, "transactionType")
    category_filter.click()
    category_filter.find_element(By.CSS_SELECTOR, "option[value='income']").click()

def test_date_range_selection(driver):
    # Wait for date inputs
    start_date = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "dateRangeStart"))
    )
    end_date = driver.find_element(By.ID, "dateRangeEnd")
    
    # Set date range
    today = datetime.now()
    start_date.send_keys(today.strftime("%Y-%m-%d"))
    end_date.send_keys((today + timedelta(days=30)).strftime("%Y-%m-%d"))
    
    # Check if transactions are filtered
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".transactions-table tbody tr"))
    )

def test_chart_updates(driver):
    # Wait for chart to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "forecast-chart"))
    )
    
    # Test forecast period selection
    period_select = driver.find_element(By.ID, "forecastPeriod")
    period_select.click()
    period_select.find_element(By.CSS_SELECTOR, "option[value='3m']").click()
    
    # Check if chart updates
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "forecast-chart"))
    )

def test_insights_display(driver):
    # Wait for insights to load
    insights = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "insight-card"))
    )
    
    assert len(insights) > 0
    
    # Check insight structure
    first_insight = insights[0]
    assert first_insight.find_element(By.CLASS_NAME, "insight-title").text
    assert first_insight.find_element(By.CLASS_NAME, "insight-description").text
    assert first_insight.find_element(By.CLASS_NAME, "insight-impact").text 