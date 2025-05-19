const projectList = [
    {
        title: "COAT: Discovery of the Hidden World with Large Language Models",
        url: "https://causalcoat.github.io/",
        icon: "fa-link"
    },
    {
        title: "LeGIT: Can Large Language Models Help Experimental Design for Causal Discovery?",
        url: "https://causalcoat.github.io/legit.html",
        icon: "fa-link"
    },
    {
        title: "On the Thinking-Language Modeling Gap in Large Language Models",
        url: "https://causalcoat.github.io/lot.html",
        icon: "fa-link"
    },
    // 可以在这里添加更多项目
];

function createProjectNav() {
    const nav = document.createElement('div');
    nav.className = 'project-nav';
    
    const dropdown = document.createElement('div');
    dropdown.className = 'dropdown';
    
    const button = document.createElement('button');
    button.className = 'dropbtn';
    button.innerHTML = `
        <span class="icon">
            <i class="fas fa-external-link-alt"></i>
        </span>
        <span>Project List</span>
    `;
    
    const content = document.createElement('div');
    content.className = 'dropdown-content';
    
    projectList.forEach(project => {
        const link = document.createElement('a');
        link.href = project.url;
        link.innerHTML = `
            <span class="icon">
                <i class="fas ${project.icon}"></i>
            </span>
            <span>${project.title}</span>
        `;
        content.appendChild(link);
    });
    
    dropdown.appendChild(button);
    dropdown.appendChild(content);
    nav.appendChild(dropdown);
    
    document.body.insertBefore(nav, document.body.firstChild);
}

document.addEventListener('DOMContentLoaded', createProjectNav);