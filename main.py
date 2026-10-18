"""Orquestador concurrente de modelos (simulado).

Ejercicio de asyncio: corrutinas, gather, timeout y semáforo.
No usa APIs reales: la latencia de red se simula con asyncio.sleep().
"""

import asyncio
import time

TIMEOUT = 2.0          # segundos máximos para toda la ejecución
MAX_SIMULTANEAS = 2    # llamadas que pueden correr a la vez (semáforo)


# --- Paso 2: tres modelos simulados, cada uno con su latencia ---
async def gpt_4_call(prompt: str, latencia: float = 1.2) -> str:
    await asyncio.sleep(latencia)
    return f"[gpt-4] respuesta a: {prompt}"


async def claude_3_call(prompt: str, latencia: float = 0.8) -> str:
    await asyncio.sleep(latencia)
    return f"[claude-3] respuesta a: {prompt}"


async def local_llama_call(prompt: str, latencia: float = 1.4) -> str:
    await asyncio.sleep(latencia)
    return f"[local-llama] respuesta a: {prompt}"


# --- Pasos 3 y 4: gather (todo a la vez) + timeout de 2 segundos ---
async def consultar_modelos(prompt: str, latencia_gpt: float = 1.2) -> None:
    inicio = time.perf_counter()
    try:
        async with asyncio.timeout(TIMEOUT):
            respuestas = await asyncio.gather(
                gpt_4_call(prompt, latencia_gpt),
                claude_3_call(prompt),
                local_llama_call(prompt),
            )
        for respuesta in respuestas:
            print(f"  {respuesta}")
    except TimeoutError:
        print(f"  ERROR: se superó el límite de {TIMEOUT}s")
    print(f"  Tiempo total: {time.perf_counter() - inicio:.2f}s")


# --- Paso 5: semáforo, 10 llamadas pero solo 2 a la vez ---
async def llamada(numero: int, semaforo: asyncio.Semaphore, t0: float) -> None:
    async with semaforo:  # si ya hay 2 dentro, espera aquí su turno
        print(f"  [{time.perf_counter() - t0:4.2f}s] llamada {numero:2d} inicia")
        await asyncio.sleep(0.3)
        print(f"  [{time.perf_counter() - t0:4.2f}s] llamada {numero:2d} termina")


async def ejecutar_lote(cantidad: int = 10) -> None:
    semaforo = asyncio.Semaphore(MAX_SIMULTANEAS)
    t0 = time.perf_counter()
    try:
        async with asyncio.timeout(TIMEOUT):
            await asyncio.gather(
                *(llamada(i, semaforo, t0) for i in range(1, cantidad + 1))
            )
    except TimeoutError:
        print(f"  ERROR: se superó el límite de {TIMEOUT}s")
    print(f"  Tiempo total: {time.perf_counter() - t0:.2f}s")


async def main() -> None:
    prompt = "¿Qué es la entropía?"

    print("=== Escenario 1: tres modelos a la vez ===")
    await consultar_modelos(prompt)

    print(f"\n=== Escenario 2: gpt-4 tarda 3s y supera el límite de {TIMEOUT}s ===")
    await consultar_modelos(prompt, latencia_gpt=3.0)

    print(f"\n=== Escenario 3: 10 llamadas, máximo {MAX_SIMULTANEAS} a la vez ===")
    await ejecutar_lote(10)


if __name__ == "__main__":
    asyncio.run(main())