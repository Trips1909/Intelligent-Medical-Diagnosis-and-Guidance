import React from "react";
import ytRecommendations from "../ytRecommendations";

const getThumbnail = (url) => {
  const videoId = url.split("v=")[1]?.split("&")[0];
  return `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
};

const YtRecommendations = ({ diagnosis }) => {
  const videos = ytRecommendations[diagnosis] || [];

  return (
    <div className="mt-6">
      <h2 className="text-xl font-bold mb-4">📺 Recommended Videos</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {videos.map((video) => (
          <a
            key={video.url}
            href={video.url}
            target="_blank"
            rel="noopener noreferrer"
            className="border rounded p-2 shadow hover:shadow-lg transition"
          >
            <img
              src={getThumbnail(video.url)}
              alt={video.title}
              className="w-full rounded"
            />
            <p className="mt-2 font-medium">{video.title}</p>
          </a>
        ))}
      </div>
    </div>
  );
};

export default YtRecommendations;
