def filter_data(api_response):
    # Extracting the required properties
    filtered_data = {
        # "info": api_response.get("data", {}).get("info"),
        "token_contract":api_response.get("data",{}).get("address"),
        "name": api_response.get("data", {}).get("name"),
        "symbol": api_response.get("data", {}).get("symbol"),
        "creationBlock": api_response.get("data", {}).get("creationBlock"),
        "metrics": api_response.get("data", {}).get("metrics")
    }

    # Filtering out empty links
    links = api_response.get("data", {}).get("links", {})
    filtered_links = {k: v for k, v in links.items() if v}
    if filtered_links:
        filtered_data["links"] = filtered_links

    # Extracting pairs with dextScore, price, and tokenRef
    pairs = api_response.get("data", {}).get("pairs", [])
    filtered_pairs = []
    for pair in pairs:
        filtered_pair = {
            "dextScore": pair.get("dextScore"),
            "tokenRef": pair.get("tokenRef")
        }
        filtered_pairs.append(filtered_pair)
    if filtered_pairs:
        filtered_data["pairs"] = filtered_pairs

    return filtered_data
 