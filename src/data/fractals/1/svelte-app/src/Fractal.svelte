<script>

    import { tick } from 'svelte';
   	import { onMount } from 'svelte';
    import * as math from 'mathjs'
    import * as d3 from 'd3'

    let status = 'ok..';

	export let iterations;

    var dataSize = 300;
    let canvas;
   	let m = { x: 0, y: 0 };

    let minx = -3
    let maxx = 5
    let miny = -3
    let maxy = 3

	function handleMousemove(event) {
		m.x = event.clientX;
		m.y = event.clientY;
	}

	function handleMousewheel(event) {
        {
            console.log(event)
            var dir = 1
            if (event.wheelDelta > 0)
                dir = -1;
            minx -= dir * 0.1 * (1 - event.offsetX / canvas.width)
            maxx += dir * 0.1 * (event.offsetX / canvas.width)
            miny -= dir * 0.1 * (1 - event.offsetY / canvas.height)
            maxy += dir * 0.1 * (event.offsetY / canvas.height)
        }
	}

    $: {
        /* these debugging statements have to be there. Otherwise, svelte won't notice that this statement "depends" on these variables, and this statement won't be called when they change*/
        console.log(canvas, iterations, minx, maxx, miny, maxy);
        status = 'calculating..'
        draw();
    }

    async function draw()
    {
        await tick();
        if (canvas)
        {
            var canvasWidth = canvas.width;
            var canvasHeight = canvas.height;
            var ctx = canvas.getContext('2d');
            var imageData = ctx.getImageData(0, 0, canvasWidth, canvasHeight);

            var buf = new ArrayBuffer(imageData.data.length);
            var buf8 = new Uint8ClampedArray(buf);
            var buf32 = new Uint32Array(buf);

            const x_factor = (maxx-minx)/(canvasWidth-1);
            const y_factor = (maxy-miny)/(canvasHeight-1);

            for (var y = 0; y < canvasHeight; ++y)
            {
                for (var x = 0; x < canvasWidth; ++x)
                {
                    /*
                    */
                    const xx = maxx - x * x_factor;
                    const yy = maxy - y * y_factor;

                    //var value = dataset[y][x];
                    var value = mandelbrot_value(xx, yy);
                    //console.log(value);

                    buf32[y * canvasWidth + x] =
                        (255 << 24) |    // alpha
                        (value / 2 << 16) |    // blue
                        (value << 8) |    // green
                        255;            // red
                }
            }

            imageData.data.set(buf8);
            ctx.putImageData(imageData, 0, 0);
        }
        status = 'ok..'
    };

    function mandelbrot_value(xx, yy)
    {
        var c = math.complex(xx, yy)
        var z = c

        for (var i = 0; i < iterations; i++)
        {
            const z_squared = math.multiply(z, z)
            z = math.add(z_squared, c)
            if (z.re + z.im > 4)
                return ~~(255*(1-i/iterations));
        }
        return 0;
    }


</script>

<main>
    <div>
        minx = {minx}
        maxx = {maxx}
        miny = {miny}
        maxy = {maxy}
        {status}
    </div>
    <canvas
        width={dataSize}
        height={dataSize}
        bind:this={canvas}
        on:mousemove={handleMousemove}
        on:mousewheel={handleMousewheel}
    >
    </canvas>
</main>
