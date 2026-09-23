import { useEffect } from 'react'
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

function FitGeoJson({ data }) {
  const map = useMap()
  useEffect(() => {
    if (!data) return
    try {
      const layer = L.geoJSON(data)
      const bounds = layer.getBounds()
      if (bounds.isValid()) map.fitBounds(bounds, { padding: [30, 30], maxZoom: 16 })
    } catch {}
  }, [data, map])
  return null
}

export default function MapView({ geojson }) {
  return (
    <MapContainer center={[20.5937, 78.9629]} zoom={5} zoomControl={false} attributionControl={true}>
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {geojson && (
        <>
          <GeoJSON
            data={geojson}
            style={() => ({ color: '#566f67', weight: 2, fillColor: '#778b80', fillOpacity: 0.22 })}
            onEachFeature={(feature, layer) => {
              const props = feature.properties || {}
              const title = props.label || props.type || 'Evidence region'
              layer.bindPopup(`<strong>${title}</strong>`)
            }}
          />
          <FitGeoJson data={geojson} />
        </>
      )}
    </MapContainer>
  )
}
