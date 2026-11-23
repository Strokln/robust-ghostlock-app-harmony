package com.sesame.app.ui

import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class Mate50PreflightTest {
    @Test
    fun `exact studied build is recognized without claiming verified root`() {
        val result = Mate50Preflight.inspect(
            model = "DCO-AL00",
            device = "HWDCO",
            buildDisplay = "DCO-AL00 4.2.0.225(C00E182)",
            kernelRelease = "5.10.136-gfdd4fb7e74b6-dirty",
            profilePresent = false,
        )
        assertTrue(result!!.sameBuildAsOfflineStudy)
        assertFalse(result.profilePresent)
    }

    @Test
    fun `missing dirty suffix is not an exact match`() {
        val result = Mate50Preflight.inspect(
            model = "DCO-AL00",
            device = "HWDCO",
            buildDisplay = "DCO-AL00 4.2.0.225(C00E182)",
            kernelRelease = "5.10.136-gfdd4fb7e74b6",
            profilePresent = true,
        )
        assertFalse(result!!.sameBuildAsOfflineStudy)
        assertTrue(result.profilePresent)
    }

    @Test
    fun `different firmware is never reported as studied build`() {
        val result = Mate50Preflight.inspect(
            model = "DCO-AL00",
            device = "HWDCO",
            buildDisplay = "DCO-AL00 4.2.0.225(C00E220)",
            kernelRelease = "5.10.136-gfdd4fb7e74b6-dirty",
            profilePresent = false,
        )
        assertFalse(result!!.sameBuildAsOfflineStudy)
    }

    @Test
    fun `retail model label is accepted without codename`() {
        val result = Mate50Preflight.inspect(
            model = "HUAWEI Mate 50 Pro",
            device = "DCO",
            buildDisplay = "DCO-AL00 4.2.0.225(C00E182)",
            kernelRelease = "5.10.136-gfdd4fb7e74b6-dirty",
            profilePresent = false,
        )
        assertTrue(result!!.sameBuildAsOfflineStudy)
    }

    @Test
    fun `unrelated phone has no Huawei panel`() {
        val result = Mate50Preflight.inspect(
            model = "Pixel 8",
            device = "shiba",
            buildDisplay = "ABC",
            kernelRelease = "5.10.136-gfdd4fb7e74b6-dirty",
            profilePresent = false,
        )
        assertNull(result)
    }
}
