import requests

from fellchensammlung.models import RescueOrganization


def sync_rescue_org_to_twenty(rescue_org: RescueOrganization, base_url, token: str):
    if rescue_org.twenty_id:
        update = True
    else:
        update = False

    payload = {
        "eMails": {
            "primaryEmail": rescue_org.email,
            "additionalEmails": None
        },
        "domainName": {
            "primaryLinkLabel": rescue_org.website,
            "primaryLinkUrl": rescue_org.website,
            "additionalLinks": []
        },
        "name": rescue_org.name,
    }

    if rescue_org.location:
        payload["address"] = {
            "addressStreet1": f"{rescue_org.location.street} {rescue_org.location.housenumber}",
            "addressCity": rescue_org.location.city,
            "addressPostcode": rescue_org.location.postcode,
            "addressCountry": rescue_org.location.countrycode,
            "addressLat": rescue_org.location.latitude,
            "addressLng": rescue_org.location.longitude,
        }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    if update:
        url = f"{base_url}/rest/companies/{rescue_org.twenty_id}"
        response = requests.patch(url, json=payload, headers=headers)
        assert response.status_code == 200
    else:
        url = f"{base_url}/rest/companies"
        response = requests.post(url, json=payload, headers=headers)
        try:
            assert response.status_code == 201
        except AssertionError:
            print(response.request.body)
            return
        rescue_org.twenty_id = response.json()["data"]["createCompany"]["id"]
        rescue_org.save()
