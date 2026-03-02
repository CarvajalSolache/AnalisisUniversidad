async function cargarDashboard() {
    const response = await fetch("datos_dashboard.json");
    const data = await response.json();

    actualizarKPIs(data.kpis);
    actualizarMaterias(data.materias_reprobacion);
    actualizarCarreras(data.carreras_promedio);
    actualizarTablaRiesgo(data.alumnos_riesgo);
}

function actualizarKPIs(kpis) {
    document.querySelectorAll("h3")[0].textContent = kpis.promedio_general;
    document.querySelectorAll("h3")[1].textContent = kpis.tasa_reprobacion + "%";
    document.querySelectorAll("h3")[2].textContent = kpis.alumnos_en_riesgo;
}

function actualizarMaterias(materias) {
    const contenedor = document.querySelector(".space-y-6");
    contenedor.innerHTML = "";

    materias.slice(0,4).forEach(m => {
        contenedor.innerHTML += `
            <div class="space-y-2">
                <div class="flex justify-between text-xs font-medium">
                    <span class="text-slate-600">${m.materia}</span>
                    <span class="text-slate-900">${m.tasa_reprobacion}%</span>
                </div>
                <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                    <div class="bg-red-400 h-full rounded-full" style="width: ${m.tasa_reprobacion}%"></div>
                </div>
            </div>
        `;
    });
}

function actualizarCarreras(carreras) {
    const contenedor = document.querySelectorAll(".space-y-6")[1];
    contenedor.innerHTML = "";

    carreras.forEach(c => {
        contenedor.innerHTML += `
            <div>
                <div class="flex justify-between text-xs mb-2">
                    <span class="text-slate-600 font-medium">${c.carrera}</span>
                    <span class="font-bold text-slate-900">${c.promedio}</span>
                </div>
                <div class="w-full bg-slate-100 h-8 rounded-lg overflow-hidden flex items-center">
                    <div class="bg-indigo-500/80 h-full rounded-r-sm"
                        style="width: ${c.promedio * 10}%"></div>
                </div>
            </div>
        `;
    });
}

function actualizarTablaRiesgo(alumnos) {
    const tbody = document.querySelector("tbody");
    tbody.innerHTML = "";

    alumnos.forEach(a => {
        tbody.innerHTML += `
            <tr class="hover:bg-slate-50 transition-colors">
                <td class="px-6 py-4 text-sm font-semibold text-slate-900">#${a.id_estudiante}</td>
                <td class="px-6 py-4 text-sm text-slate-600">${a.carrera}</td>
                <td class="px-6 py-4 text-sm text-slate-600">${a.materia}</td>
                <td class="px-6 py-4 text-center">
                    <span class="text-sm font-bold text-red-600">${a.calificacion}</span>
                </td>
                <td class="px-6 py-4 text-right">
                    <span class="px-2 py-0.5 rounded-full bg-red-100 text-red-700 text-[10px] font-bold">
                        ALERTA
                    </span>
                </td>
            </tr>
        `;
    });


function exportarCSV() {
    // Seleccionamos todas las filas del tbody
    const filas = document.querySelectorAll("tbody tr");
    
    // Encabezados del CSV
    const datos = [["id_estudiante","carrera","materia","calificacion","semestre","año"]];

    // Recorremos cada fila de la tabla
    filas.forEach(fila => {
        const columnas = fila.querySelectorAll("td");
        // Extraemos los datos visibles
        const id = columnas[0].textContent.replace("#","").trim(); // quitamos #
        const carrera = columnas[1].textContent.trim();
        const materia = columnas[2].textContent.trim();
        const calificacion = columnas[3].textContent.trim();

        // Semestre y año: si no están en la tabla, puedes asignar valores por defecto
        const semestre = "1"; // o extraerlo de tu JSON si lo tienes
        const año = "2024";   // o extraer dinámicamente

        datos.push([id, carrera, materia, calificacion, semestre, año]);
    });

    // Convertimos a CSV
    const csvContent = datos.map(e => e.join(",")).join("\n");

    // Creamos enlace para descargar
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "alumnos_riesgo.csv");
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Conectamos con el botón
document.getElementById("btnExport").addEventListener("click", exportarCSV);
}

cargarDashboard();