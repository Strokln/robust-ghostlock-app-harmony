package com.sesame.app.ui

/**
 * Read-only identity check for the Huawei Mate 50 Pro research target.
 *
 * This is deliberately independent from profile resolution and the native runtime.
 * Matching a kernel banner or having an imported profile must never be treated as
 * evidence that a privilege-escalation route is safe or has succeeded.
 */
internal object Mate50Preflight {
    const val TARGET_MODEL = "DCO-AL00"
    const val TARGET_DEVICE = "HWDCO"
    const val TARGET_BUILD = "4.2.0.225(C00E182)"
    const val TARGET_KERNEL = "5.10.136-gfdd4fb7e74b6-dirty"

    fun inspect(
        model: String,
        device: String,
        buildDisplay: String,
        kernelRelease: String,
        profilePresent: Boolean,
    ): Result? {
        // Global ROMs often expose a retail model name instead of DCO-AL00.
        val normalizedModel = model.filterNot(Char::isWhitespace)
        val retailMate50 = normalizedModel.contains("Huawei", ignoreCase = true) &&
            normalizedModel.contains("Mate50Pro", ignoreCase = true)
        val isMate50 = model.equals(TARGET_MODEL, ignoreCase = true) ||
            device.equals(TARGET_DEVICE, ignoreCase = true) ||
            retailMate50
        if (!isMate50) return null

        return Result(
            firmwareMatches = buildDisplay.contains(TARGET_BUILD, ignoreCase = true),
            kernelMatches = kernelRelease == TARGET_KERNEL,
            profilePresent = profilePresent,
        )
    }

    data class Result(
        val firmwareMatches: Boolean,
        val kernelMatches: Boolean,
        val profilePresent: Boolean,
    ) {
        // An exact identity match is not a verified route or a successful exploit.
        val sameBuildAsOfflineStudy: Boolean get() = firmwareMatches && kernelMatches
    }
}
