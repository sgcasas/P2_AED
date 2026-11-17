// BFS 0-1: caminos minimos desde un origen en un grafo dirigido con pesos 0 o 1.
// Imprime por stdout un JSON con el grafo y cada paso de la ejecucion.
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
using namespace std;

const int INF = 1e9;

// Deque propia con buffer circular (no usamos std::deque).
struct Deque {
    vector<int> buf;
    int head = 0, sz = 0;
    Deque(int cap) : buf(cap) {}
    bool empty() const { return sz == 0; }
    void push_front(int x) { head = (head - 1 + buf.size()) % buf.size(); buf[head] = x; sz++; }
    void push_back(int x) { buf[(head + sz) % buf.size()] = x; sz++; }
    int pop_front() { int x = buf[head]; head = (head + 1) % buf.size(); sz--; return x; }
    vector<int> items() const {
        vector<int> v;
        for (int i = 0; i < sz; i++) v.push_back(buf[(head + i) % buf.size()]);
        return v;
    }
};

struct Edge { int u, v, w; };

string arr(const vector<int>& a, bool inf_as_null = false) {
    string s = "[";
    for (size_t i = 0; i < a.size(); i++) {
        if (i) s += ",";
        s += (inf_as_null && a[i] == INF) ? "null" : to_string(a[i]);
    }
    return s + "]";
}

string edge(const Edge& e) {
    return "{\"u\":" + to_string(e.u) + ",\"v\":" + to_string(e.v) + ",\"w\":" + to_string(e.w) + "}";
}

int main(int argc, char* argv[]) {
    if (argc < 2) { cerr << "Uso: ./bfs01 <archivo_entrada>\n"; return 1; }
    ifstream in(argv[1]);
    if (!in) { cerr << "No se pudo abrir " << argv[1] << "\n"; return 1; }

    int n, m, s;
    in >> n >> m >> s;
    vector<Edge> edges(m);
    vector<vector<int>> adj(n); // indices de aristas que salen de cada nodo
    for (int i = 0; i < m; i++) {
        in >> edges[i].u >> edges[i].v >> edges[i].w;
        adj[edges[i].u].push_back(i);
    }

    vector<int> dist(n, INF), parent(n, -1);
    vector<bool> done(n, false);
    Deque dq(m + 2); // cada push viene de una relajacion exitosa: a lo mas m + 1
    vector<string> steps;

    auto state = [&]() {
        return "\"deque\":" + arr(dq.items()) + ",\"dist\":" + arr(dist, true) + ",\"parent\":" + arr(parent);
    };

    dist[s] = 0;
    dq.push_back(s);
    steps.push_back("{\"type\":\"init\",\"node\":" + to_string(s) + "," + state() + "}");

    while (!dq.empty()) {
        int u = dq.pop_front();
        if (done[u]) { // salida desactualizada: u ya se proceso con su distancia final
            steps.push_back("{\"type\":\"stale\",\"node\":" + to_string(u) + "," + state() + "}");
            continue;
        }
        done[u] = true;
        steps.push_back("{\"type\":\"pop\",\"node\":" + to_string(u) + "," + state() + "}");

        for (int id : adj[u]) {
            Edge& e = edges[id];
            if (dist[u] + e.w < dist[e.v]) {
                int old = dist[e.v];
                dist[e.v] = dist[u] + e.w;
                parent[e.v] = u;
                string side = (e.w == 0) ? "front" : "back";
                if (e.w == 0) dq.push_front(e.v); else dq.push_back(e.v);
                steps.push_back("{\"type\":\"relax\",\"edge\":" + edge(e) +
                    ",\"old\":" + (old == INF ? string("null") : to_string(old)) +
                    ",\"new\":" + to_string(dist[e.v]) + ",\"push\":\"" + side + "\"," + state() + "}");
            } else {
                steps.push_back("{\"type\":\"no_improve\",\"edge\":" + edge(e) + "," + state() + "}");
            }
        }
    }
    steps.push_back("{\"type\":\"done\"," + state() + "}");

    // Salida JSON
    cout << "{\n  \"graph\": {\"n\":" << n << ",\"source\":" << s << ",\"edges\":[";
    for (int i = 0; i < m; i++) cout << (i ? "," : "") << edge(edges[i]);
    cout << "]},\n  \"steps\": [\n";
    for (size_t i = 0; i < steps.size(); i++) cout << "    " << steps[i] << (i + 1 < steps.size() ? ",\n" : "\n");
    cout << "  ]\n}\n";
    return 0;
}
