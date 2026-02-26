async function loadProgressions() {
    const progs = await api('/api/progressions');
    const container = document.getElementById('progressions-list');

    container.innerHTML = progs.map(prog => {
        const totalSteps = prog.steps.length;
        const currentStep = prog.current_step;
        const isComplete = currentStep > totalSteps;

        const stepsHtml = prog.steps.map((step, i) => {
            const stepNum = i + 1;
            let nodeClass = 'step-node';
            let labelClass = 'step-label';
            let connectorClass = 'step-connector';

            if (stepNum < currentStep) {
                nodeClass += ' completed';
                labelClass += ' completed';
                connectorClass += ' completed';
            } else if (stepNum === currentStep) {
                nodeClass += ' current';
                labelClass += ' current';
            }

            const connector = i < totalSteps - 1
                ? `<div class="${connectorClass}"></div>` : '';

            return `
                <div class="progression-step">
                    <div class="${nodeClass}">${stepNum}</div>
                    <div class="${labelClass}">${step.exercise_name}</div>
                    <button class="btn-demo" style="margin-top:4px" onclick="showVideoModal('${step.exercise_name.replace(/'/g, "\\'")}')">Demo</button>
                </div>
                ${connector}
            `;
        }).join('');

        return `
            <div class="card progression-tree">
                <div class="card-header">
                    <div>
                        <h3>${prog.name}</h3>
                        <span class="text-muted text-sm">${prog.description || ''}</span>
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-sm" onclick="regressProgression(${prog.id})"
                            ${currentStep <= 1 ? 'disabled' : ''}>&#8592; Back</button>
                        <button class="btn btn-sm btn-primary" onclick="advanceProgression(${prog.id})"
                            ${currentStep >= totalSteps ? 'disabled' : ''}>Advance &#8594;</button>
                    </div>
                </div>
                <div class="text-sm mb-8 text-muted">
                    Step ${Math.min(currentStep, totalSteps)} of ${totalSteps}
                    ${currentStep <= totalSteps && prog.steps[currentStep - 1]
                        ? ` — Current: <strong style="color:var(--primary)">${prog.steps[currentStep - 1].exercise_name}</strong>`
                        : ' — Completed!'}
                    ${currentStep <= totalSteps && prog.steps[currentStep - 1]
                        ? `<br>Goal: ${prog.steps[currentStep - 1].criteria}` : ''}
                </div>
                <div class="progression-steps">${stepsHtml}</div>
            </div>
        `;
    }).join('');
}

async function advanceProgression(id) {
    await api(`/api/progressions/${id}/advance`, { method: 'POST' });
    showToast('Level up! Keep pushing!');
    loadProgressions();
}

async function regressProgression(id) {
    await api(`/api/progressions/${id}/regress`, { method: 'POST' });
    showToast('Stepped back');
    loadProgressions();
}

loadProgressions();
