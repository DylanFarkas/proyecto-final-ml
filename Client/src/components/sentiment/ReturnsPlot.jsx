import { useEffect, useState } from "react";
import { getPlot } from "../../api/sentimentAPI";


export default function ReturnsPlot() {
  const [imgSrc, setImgSrc] = useState(null);

  useEffect(() => {
    getPlot()
      .then((res) => {
        const url = URL.createObjectURL(res.data);
        setImgSrc(url);
      })
      .catch((err) => console.error("Error fetching plot:", err));
  }, []);

  return imgSrc ? <img src={imgSrc} alt="Returns Plot" /> : <p>Cargando gráfico...</p>;
}
