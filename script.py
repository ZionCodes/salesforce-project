from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re

# Read the CSV file
csv_file = 'NH_ProviderInfo_Sep2025 - filtered.csv'
df = pd.read_csv(csv_file)

all_providers = df.iloc[0:142]

results = []

# Initialize Selenium
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    for index, row in all_providers.iterrows():
        provider_name = row.iloc[1]  # Column B (Provider Name)
        cms_number = row.iloc[0] if len(row) > 0 else ''  # Column A (CMS Number)
        
        print(f"\n[{index+1}/142] Processing: {provider_name}")
        
        try:
            # Build search URL
            search_query = provider_name.replace(' ', '+')
            search_url = f"https://azcarecheck.azdhs.gov/s/?programType=Health+Care+Facilities&licenseType=All&facilityStatus=Active&licenseStatus=Active&searchQuery={search_query}"
            
            # Navigate to search URL
            driver.get(search_url)
            time.sleep(5)  # Wait for JavaScript to render
            
            # Find the "Get Details" link
            detail_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Get Details')]")
            
            if detail_links:
                detail_url = detail_links[0].get_attribute('href')
                print(f"✓ Found detail URL")
                
                # Navigate to detail page to extract admin info
                driver.get(detail_url)
                time.sleep(5)
                
                # Extract administrator data
                admin_name = ''
                admin_title = ''
                phone = ''
                facility_address = ''
                license_number = ''
                inferred_email = ''
                
                try:
                    # Get all text from the page
                    body_text = driver.find_element(By.TAG_NAME, 'body').text
                    lines = body_text.split('\n')
                    
                    # Parse the page content
                    for i, line in enumerate(lines):
                        if 'Chief Administrative Officer' in line:
                            admin_title = 'Chief Administrative Officer'
                            if i + 1 < len(lines):
                                admin_name = lines[i + 1].strip()
                        elif line.strip() == 'Phone':
                            if i + 1 < len(lines):
                                phone = lines[i + 1].strip()
                        elif line.strip() == 'Address':
                            if i + 1 < len(lines):
                                facility_address = lines[i + 1].strip()
                        elif line.strip() == 'License':
                            if i + 1 < len(lines) and 'NCI-' in lines[i + 1]:
                                license_number = lines[i + 1].strip()
                    
                    # Infer email address (BONUS!)
                    if admin_name:
                        name_parts = admin_name.lower().split()
                        if len(name_parts) >= 2:
                            first_name = name_parts[0]
                            last_name = name_parts[-1]
                            
                            # Create domain from facility name
                            facility_clean = provider_name.lower()
                            facility_clean = re.sub(r'\b(the|of|and|center|rehab|rehabilitation|healthcare|health care|nursing|home)\b', '', facility_clean)
                            facility_clean = re.sub(r'[^a-z0-9]', '', facility_clean)
                            
                            inferred_email = f"{first_name}.{last_name}@{facility_clean}.com"
                    
                    print(f"✓ Administrator: {admin_name}")
                    print(f"  Title: {admin_title}")
                    print(f"  Phone: {phone}")
                    print(f"  Email: {inferred_email}")
                    
                    results.append({
                        'Provider_Name': provider_name,
                        'CMS_Number': cms_number,
                        'Detail_URL': detail_url,
                        'Admin_Name': admin_name,
                        'Admin_Title': admin_title,
                        'Phone': phone,
                        'Facility_Address': facility_address,
                        'License_Number': license_number,
                        'Inferred_Email': inferred_email,
                        'Status': 'Success',
                        'Error': ''
                    })
                    
                except Exception as e:
                    print(f"✗ Error extracting admin data: {str(e)}")
                    results.append({
                        'Provider_Name': provider_name,
                        'CMS_Number': cms_number,
                        'Detail_URL': detail_url,
                        'Admin_Name': '',
                        'Admin_Title': '',
                        'Phone': '',
                        'Facility_Address': '',
                        'License_Number': '',
                        'Inferred_Email': '',
                        'Status': 'Failed',
                        'Error': f'Data extraction error: {str(e)}'
                    })
            else:
                print(f"✗ No 'Get Details' link found")
                results.append({
                    'Provider_Name': provider_name,
                    'CMS_Number': cms_number,
                    'Detail_URL': '',
                    'Admin_Name': '',
                    'Admin_Title': '',
                    'Phone': '',
                    'Facility_Address': '',
                    'License_Number': '',
                    'Inferred_Email': '',
                    'Status': 'Failed',
                    'Error': 'No Get Details link found'
                })
                
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Error: {error_msg}")
            results.append({
                'Provider_Name': provider_name,
                'CMS_Number': cms_number,
                'Detail_URL': '',
                'Admin_Name': '',
                'Admin_Title': '',
                'Phone': '',
                'Facility_Address': '',
                'License_Number': '',
                'Inferred_Email': '',
                'Status': 'Failed',
                'Error': error_msg
            })
            
except Exception as e:
    print(f"Fatal error: {str(e)}")
    
finally:
    driver.quit()
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    # Save results to CSV
    output_df = pd.DataFrame(results)
    output_df.to_csv('az_administrators_enriched.csv', index=False)
    print(f"✓ Results saved to 'az_administrators_enriched.csv'")
    print(f"✓ Successfully processed: {len([r for r in results if r['Status'] == 'Success'])}/142")
    print(f"✗ Failed: {len([r for r in results if r['Status'] == 'Failed'])}/142")