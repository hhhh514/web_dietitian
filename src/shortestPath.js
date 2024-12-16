
function dijkstra(attractions) {
  const n = attractions.length;
  const dist = Array(n).fill(Infinity);
  const visited = Array(n).fill(false);
  const result = [];
  dist[0] = 0; // 起點設為第一個景點
  var totalTime=0;
  for (let i = 0; i < n; i++) {
    let u = -1;
    for (let j = 0; j < n; j++) {
      if (!visited[j] && (u === -1 || dist[j] < dist[u])) {
        u = j;
      }
    }
    if (dist[u] === Infinity) break;
    visited[u] = true;
    result.push(attractions[u].name);
    for (let v = 0; v < n; v++) {
      if(attractions[v].waitTime >= attractions[v].path){
        totalTime=attractions[v].waitTime;
      }else{
        totalTime=attractions[v].waitTime*2;
      }
      if (!visited[v] && dist[u] + totalTime < dist[v]) {
        dist[v] = dist[u] + totalTime;
      }
    }
  }
  return result;
}

export {dijkstra };