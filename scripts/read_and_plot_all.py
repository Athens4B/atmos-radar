def plot_radar_with_bounds(radar, field, site_id):
    print(f"🖼️ Plotting {field} for {site_id}...")

    sweep = 0
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_below(field, 5)
    gatefilter.exclude_invalid(field)

    data = radar.fields[field]["data"]
    mask = gatefilter.gate_excluded
    filtered_data = np.ma.masked_where(mask, data)

    # Extract sweep slice
    sweep_slice = radar.get_slice(sweep)
    reflectivity = filtered_data[sweep_slice]

    # Get lat/lon from supported method
    lats, lons, _ = radar.get_gate_lat_lon_alt(sweep)

    # Compute bounds
    lat0 = radar.latitude['data'][0]
    lon0 = radar.longitude['data'][0]
    max_range_km = radar.range['data'][-1] / 1000.0
    delta = max_range_km / 111.0

    bounds = {
        "west": lon0 - delta,
        "east": lon0 + delta,
        "south": lat0 - delta,
        "north": lat0 + delta
    }

    bounds_path = f"../static/{site_id}_radar_bounds.json"
    with open(bounds_path, "w") as f:
        json.dump(bounds, f)
    print(f"✅ Saved bounds to {bounds_path}")

    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    ax.pcolormesh(lons, lats, reflectivity, cmap="NWSRef", vmin=-32, vmax=64)
    ax.axis("off")
    ax.set_aspect("equal", "box")

    image_path = f"../static/{site_id}_radar_reflectivity.png"
    plt.savefig(image_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    print(f"✅ Saved image to {image_path}")
