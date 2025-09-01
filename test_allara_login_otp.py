# test_allara_login_otp.py

def test_login_page_renders(driver, base_url):
    driver.get(base_url)
    # Page should open and have a non-empty title
    assert driver.title.strip() != ""
