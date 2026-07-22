import os

files = [
    'src/components/AiAssistantView.tsx',
    'src/components/PackageBuilderView.tsx',
    'src/components/DashboardView.tsx',
    'src/components/IndividualPricingView.tsx'
]

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = content.replace('\\`', '`')
    content = content.replace('\\$', '$')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
print('Fixed escaping issues.')
